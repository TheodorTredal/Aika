

'''Må finne ut hvorfor vi har RAFT i AIKA'''

class RaftNode:
    '''RAFT protocol is implemented as the cluster controller.'''
    def __init__(self):
        self.log = []
        self.IsLeader = False
        self.TimeToLive = 0
