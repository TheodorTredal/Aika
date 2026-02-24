import sys
from raftNode import RaftNode
from localController import LocalController



def main():
    '''Startup script, get the raft and local controller nodes started'''

    if len(sys.argv) < 3:
        print("Usage: python startChordNode.py <host> <port>") 
        sys.exit(1) 

        host = sys.argv[1]
        port = int(sys.argv[2])


        localControllerNode = LocalController(host=host, port=port)

        