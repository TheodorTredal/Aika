from flask import Flask, jsonify, request
import requests
from enum import Enum
import time
import random
import threading


class RaftStates(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"


'''Må finne ut hvorfor vi har RAFT i AIKA'''


class RaftNode:
    '''RAFT protocol is implemented as the cluster controller.'''
    def __init__(self, host: str, port: int, otherRaftNodes: list):


        # Persistent state on all servers
        self.currentTerm = 0
        self.votedFor = None
        self.log = []
        self.state = RaftStates.FOLLOWER # Every Raft server initializes as follower
        self.leader = None

        # list of votes when in candidate state
        self.myVotes = []
        self.cluster_size = len(otherRaftNodes) + 1

        # Volatile state on all servers
        self.commitIndex = 0 # Index of highest log entry known to be committed (init to 0, increases monotonically)
        self.lastApplied = 0 # Index of highest log entry applied to state machine (init to 0, increases monotonically)

        # Volatile state on leaders (Reinitialized after election)
        self.nextIndex = [] # Index of the next log entry to send to that server (init to leader last log index + 1)
        self.matchIndex = [] # Index of highes log entry known to be replicated on server (inited to 0, increases monotonically)

        self.last_heartbeat = time.time()
        self.timeout_ms = random.uniform(0.150, 0.600) # asumes that no two raft node has the same timeout 


        # Cluster addresses
        self.host = host
        self.port = port
        self.alive = True
        self.otherRaftNodes: list = otherRaftNodes
        self.app = Flask(__name__)
        self.setup_routes()


    def setup_routes(self):

        @self.app.route("/list-raft-nodes", methods=["GET"])
        def list_raft_nodes():
            return jsonify({
                "nodes": self.otherRaftNodes
            })

        @self.app.route("/raft-node-info", methods=["GET"])
        def raft_node_info():
            return jsonify({ 
                "state": self.state.value,
                "currentTerm": self.currentTerm,
                "votedFor": self.votedFor,
                "commitIndex": self.commitIndex,
                "lastApplied": self.lastApplied,
                "nextIndex": self.nextIndex,
                "matchIndex": self.matchIndex,
                "otherRaftNodes": self.otherRaftNodes,
                "server_id": f"{self.host}:{self.port}",
                "myVotes": self.myVotes,
                "leader": self.leader,
                "alive": self.alive
                })
        
        @self.app.route("/raft-state-info", methods=["GET"])
        def raft_state_info():
            return jsonify({
                "ID": f"{self.host}:{self.port}",
                "state": self.state.value
            })
        
        @self.app.route("/raft-myVote", methods=["GET"])
        def raft_my_vote_info():
            return jsonify({
                "server_id": f"{self.host}:{self.port}",
                "myVotes": self.myVotes,
                "VotedFor": self.votedFor,
                "term": self.currentTerm,
                "ID": f"{self.host}:{self.port}",
                "state": self.state.value
            })
        

        ### TEST DEBUG API KALL

        @self.app.route("/raft-change-status", methods=["POST"])
        def change_raft_node_status():
            '''
            Changes the state of a RAFT node

            state = 1: Follower
            state = 2: Candidate
            state = 3: Leader
            
            How to use: "curl -X POST http://c0-0:0000/raft-change-status?state=1"'''
            
            state = request.args.get("state", type=int)
            
            if state == 1:
                self.state = RaftStates.FOLLOWER

            elif state == 2:
                self.state = RaftStates.CANDIDATE

            elif state == 3:
                self.state = RaftStates.LEADER

            else:
                return {"400": "Bad Request"}
            
            return {
                "success": True,
                "new_state": self.state.value
            }, 200
            

        @self.app.route("/raft-kill-node", methods=["POST"])
        def kill_node():
            '''Alives or unalives a raft node.
            
            alive_status = 0: Dead
            alive_status = 1: Alive

            How to use "curl -X POST http://c0-0:0000/raft-kill-node?alive=0"
            '''


            alive = request.args.get("alive", type=int)

            if  alive == 0:
                self.alive = False

            elif alive == 1:
                self.alive = True

            else:
                return {"400": "Bad Request"}
            
            return {
                "success": True,
                "alive_status": self.alive
            }
        

        ####### Faktiske RAFT funksjoner
        # Lederen sender data til dette API kallet
        @self.app.route("/raft-appendEntries", methods=["POST"])
        def appendEntries():

            # Receive data from the leader
            data = request.json
            self.handle_append_entries(data)

            # Send ACK tilbake til lederen
            return {"success": True}, 200
        

        @self.app.route("/requestVote", methods=["POST"])
        def send_vote():
            if self.votedFor is not None:
                return

            data = request.json

            # newer term -> reset the vote
            if data["term"] > self.currentTerm:
                self.currentTerm = data["term"] # Update this node's term
                # self.votedFor = None # Stemme resetter ved nytt term
                self.state = RaftStates.FOLLOWER
                self.votedFor = data["candidateID"] # addressen til candidate. Stem på den nye kandidaten
                self.request_vote_handler(data["candidateID"]) # Send the vote back to the candidate


            # if self.votedFor is None and data["term"] == self.currentTerm:


        @self.app.route("/candidate-recv-votes", methods=["POST"])
        def recv_vote():
            '''Endpoint for the candidate to receive votes from followers'''

            data = request.json
            self.myVotes.append(data["voter"])






    def request_vote_handler(self, candidateID):
        '''Here the follower sends its vote back to the candidate'''

        url = f"http://{candidateID}/candidate-recv-votes"

        requests.post(url=url, json={
            "voter": f"{self.host}:{self.port}"
        })


    def handle_append_entries(self, data):
        '''The leader will post some data, and the follower will reset it's
            timer
        '''

        term = data["term"]

        if term >= self.currentTerm:
            self.leader = data["leaderId"]
            self.currentTerm = term
            self.state = RaftStates.FOLLOWER
            self.reset_election_timer()


    def reset_election_timer(self):
        self.last_heartbeat = time.time()


    def follower_loop(self):
        '''If the timer runs out we start an election'''

        # Election timer loop
        if time.time() - self.last_heartbeat > self.timeout_ms:
            '''If the timer runs out, change the state to candidate
                increase the term, vote on myself
            '''
            self.become_candidate()


    def become_candidate(self):
        '''Sets status to candidate, sends out requestVote to every other server'''

        self.state = RaftStates.CANDIDATE

        self.currentTerm += 1 # Increment the term

        if self.votedFor is None:
            self.votedFor = f"{self.host}:{self.port}" # Register this raft node's vote
            self.myVotes.append(f"{self.host}:{self.port}") # Vote for myself


        for node_addr in self.otherRaftNodes:
            url = f"http://{node_addr}/requestVote"
            requests.post(url=url, json={
                            "candidateID": f"{self.host}:{self.port}",
                            "term": self.currentTerm  
                          })
            
        # Reset the election timer
        self.reset_election_timer()
            



    def candidate_loop(self):
        '''If the RAFT node gets the majority of the votes, 
        this node becomes the leader'''

        '''Hvis noder returner addressen til kandiaten så har den fått en stemme
            Får kandidat noden n / 2 + 1 stemme så vinner den og blir leader
        '''


        # Send voting request to other raft nodes.

            
        # cluster_size = len(self.otherRaftNodes) + 1

        # After sending requestVote Put the candidate node in a waiting state, 
        # waiting for either
        # a. A majority vote, change state to leader and return to running_loop
        # b. Or appendEntries from a server (claiming to be leader) that has a term atleast as large as
        #      This candidate's term, this node will recognize the leader and return to follower state
        # c. a stalemate, new term, new elecetion

        
        #  case a.
        if len(self.myVotes) >= (self.cluster_size // 2) + 1:
            self.state = RaftStates.LEADER
            self.leader = f"{self.host}:{self.port}"
            return

        #  case b.



        #  case c.
        if time.time() - self.last_heartbeat > self.timeout_ms:
            self.become_candidate()

        
        


    def leader_loop(self):

        # Send out heartbeats to all followers
        for node_addr in self.otherRaftNodes:
            url = f"http://{node_addr}/raft-appendEntries"
            requests.post(url, json={
                "term": self.currentTerm,
                "leaderId": f"{self.host}:{self.port}",
                "entries": []
            })

        time.sleep(0.05) # 50 ms heartbeat


    def running_loop(self):
        '''The raft nodes does different things depending on which state they are in
            This method is trying to keep the different states cleanly separated.
        '''

        def run():
            while True:
                if self.state == RaftStates.FOLLOWER:
                    self.follower_loop()

                if self.state == RaftStates.CANDIDATE:
                    self.candidate_loop()

                if self.state == RaftStates.LEADER:
                    self.leader_loop()

                time.sleep(0.01)

        threading.Thread(target=run, daemon=True).start()




    def init(self):
        '''The node is always running, if alive is set to False, 
        the node is for all intents and purposes not shutdown and can be considered killed / crashed'''
        
        self.app.run(
            host=self.host,
            port=self.port,
            debug=True, 
            use_reloader=False)
