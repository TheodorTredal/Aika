import sys
from raftNode import RaftNode

def main():
    '''Startup for all the Raft nodes, each node gets their own host + port, including a list of other RAFT nodes'''

    if len(sys.argv) < 4:
        print("Usage: python startChordNode.py <host> <port> <otherRaftNodes>") 
        sys.exit(1) 

    host = sys.argv[1]
    port = int(sys.argv[2])
    otherRaftNodes = sys.argv[3]


    thisRaftNode = RaftNode(host=host, port=port, otherRaftNodes=otherRaftNodes)
    thisRaftNode.init()





if __name__ == "__main__":
    main()

