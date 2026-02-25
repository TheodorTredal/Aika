from flask import Flask, jsonify, request
import requests
from enum import Enum
import time
import random

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
        self.state = RaftStates.FOLLOWER
        self.leader = None

        # list of votes when in candidate state
        self.myVotes = []

        # Volatile state on all servers
        self.commitIndex = 0 # Index of highest log entry known to be committed (init to 0, increases monotonically)
        self.lastApplied = 0 # Index of highest log entry applied to state machine (init to 0, increases monotonically)

        # Volatile state on leaders (Reinitialized after election)
        self.nextIndex = [] # Index of the next log entry to send to that server (init to leader last log index + 1)
        self.matchIndex = [] # Index of highes log entry known to be replicated on server (inited to 0, increases monotonically)

        self.last_heartbeat = time.time()
        self.timeout_ms = random.uniform(150, 300)

        # Cluster addresses
        self.host = host
        self.port = port
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
                "address": f"{self.host}:{self.port}"
                })
        
        @self.app.route("/raft-state-info", methods=["GET"])
        def raft_state_info():
            return jsonify({
                "state": self.state.value
            })
        

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

                data = request.json

                if data["term"] < self.currentTerm:
                    self.votedFor = data["candidateId"] # addressen til candidate
                    self.currentTerm = data["term"] # Update this node's term
                    # Return ACK to the candidate
                    self.request_vote_handler(data["candidateId"])


        @self.app.route("/candidate-recv-votes", methods=["POST"])
        def recv_vote():
            '''The candidate recveives votes from the follower'''

            data = request.json()
            self.myVotes.append(data["voter"])


            


    # def appendEntries(self, term, leaderId, prevLogIndex, prevLogTerm, entries: list, leadercommit):
    #     """AppendEntries RPC

    #         Invoked by the leader to replicate log entries; also used as heartbeat

    #         term: leader's term
    #         leaderId: so follower can redirect clients
    #         prevLogIndex: index of log entry immediately preceding
    #         prevLogTerm: term of prevLogIndex entry
    #         entries[]: log entries to store (empty for heartbeat)
    #         leaderCommit: leader's commitIndex


    #         Results
    #             Term: currentTerm, for leader to update itself
    #             success: true if follower contained entry matching prevLogIndex and prevLogTerm
    #     """


    #     # 1. reply false 
    #     if term < self.currentTerm:
    #         pass

    #     # 2. reply false
    #     if prevLogIndex not in self.log:
    #         pass


    #     # 3. Se side 4. i RAFT artikkelen https://raft.github.io/raft.pdf

    #     # 4. 

    #     # 5.

    # def requestVote(self, term, candidateId, lastLogIndex, lastLogTerm):
    #     '''
    #     Docstring for requestVote
        
    #     :param self: Description
    #     :param term: Description
    #     :param candidateId: Description
    #     :param lastLogIndex: Description
    #     :param lastLogTerm: Description
        
    #     Results
    #         term: currentTerm, for candidate to update itself
    #         voteGranted: true means candidate received vote
    #     '''

    #     # Reply false
    #     if term < self.currentTerm:
    #         pass


    #     # if self.votedFor is None or candidateId and candidate's lgo is at least as up tp date as receiver's log,  grant vote



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
            self.state = RaftStates.CANDIDATE



    def candidate_loop(self):
        '''If the RAFT node gets tje majority of the votes, 
        this node becomes the leader'''

        '''Hvis noder returner addressen til kandiaten så har den fått en stemme
            Får kandidat noden n / 2 + 1 stemme så vinner den og blir leader
        '''


        self.currentTerm += 1 # Increment the term
        self.myVotes.append(f"{self.host}:{self.port}") # Vote for myself

        # Send voting request to other raft nodes.
        for node_addr in self.otherRaftNodes:
            url = f"http://{node_addr}/requestVote"
            requests.post(url=url, json={
                            "candidateId": f"{self.host}:{self.port}",
                            "term": self.currentTerm  
                          })
            

        # After sending requestVote Put the candidate node in a waiting state, 
        # waiting for either
        # a. A majority vote, change state to leader and return to running_loop
        # b. Or appendEntries from a server (claiming to be leader) that has a term atleast as large as
        #      This candidate's term, this node will recognize the leader and return to follower state
        # c. a stalemate, new term new elecetion
        while 1: 
        
            #  case a.
            if len(self.myVotes) < len(self.otherRaftNodes) // 2 + 1:
                self.state = RaftStates.LEADER
                return

            #  case b.



            #  case c.




    def leader_loop(self):

        # Send ut heartbeats til alle følgerne
        for node_addr in self.otherRaftNodes:
            url = f"http://{node_addr}/raft-appendEntries"
            request = requests.post(url, json={
                "term": self.currentTerm,
                "leaderId": f"{self.host}:{self.port}",
                "entries": []
            })

        time.sleep(0.05) # 50 ms heartbeat



    def running_loop(self):
        '''The raft nodes does different things depending on which state they are in
            This method is trying to keep the different states cleanly separated.
        '''

        while True:
            if self.state == RaftStates.FOLLOWER:
                self.follower_loop()

            if self.state == RaftStates.CANDIDATE:
                self.candidate_loop()

            if self.state == RaftStates.LEADER:
                self.leader_loop()

            time.sleep(0.01)




    def init(self):
        '''The node is always running, if alive is set to False, 
        the node is for all intents and purposes not shutdown and can be considered killed / crashed'''
        
        self.app.run(
            host=self.host,
            port=self.port,
            debug=True, 
            use_reloader=False)





