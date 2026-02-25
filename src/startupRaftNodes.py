import sys
from raftNode import RaftNode

def main():
    '''Startup for all the Raft nodes, each node gets their own host + port, including a list of other RAFT nodes'''

    if len(sys.argv) < 3:
        print("Usage: python startChordNode.py <host> <port>") 
        sys.exit(1) 

    host = sys.argv[1]
    port = int(sys.argv[2])


    # Fetch all other raft node addresses.
    otherRaftNodes = []
    with open("../data/activehostport.txt", "r") as file:
            for node_addr in file:
                # Do not include this node in the otherRaftNodes list
                if node_addr.strip().replace("/", "") != f"{host}:{port}":
                    otherRaftNodes.append(node_addr.strip().replace("/", ""))


    thisRaftNode = RaftNode(host=host, port=port, otherRaftNodes=otherRaftNodes)
    thisRaftNode.running_loop()
    thisRaftNode.init()





if __name__ == "__main__":
    main()

