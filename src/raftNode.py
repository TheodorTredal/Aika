from flask import Flask, request, jsonify
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

        # Volatile state on all servers
        self.commitIndex = 0 # Index of highest log entry known to be committed (init to 0, increases monotonically)
        self.lastApplied = 0 # Index of highest log entry applied to state machine (init to 0, increases monotonically)

        # Volatile state on leaders (Reinitialized after election)
        self.nextIndex = [] # Index of the next log entry to send to that server (init to leader last log index + 1)
        self.matchIndex = [] # Index of highes log entry known to be replicated on server (inited to 0, increases monotonically)

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
                "state": self.state,
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
                "state": self.state
            })


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


        # if self.votedFor is None or candidateId and candidate's lgo is at least as up tp date as receiver's log,  grant vote


    


    def running_loop(self):

        while True:
            timeout_ms = random.randint(150, 300)
            election_deadline = time.time() + timeout_ms / 1000

            # Venter på svar fra lederen
            while time.time() < election_deadline:

                # Hvis man får svar fra lederen -> break
                if self.leader is not None:


                    pass


    def init(self):
        '''The node is always running, if alive is set to False, 
        the node is for all intents and purposes not shutdown and can be considered killed / crashed'''
        
        self.app.run(
            host=self.host,
            port=self.port,
            debug=True, 
            use_reloader=False)





