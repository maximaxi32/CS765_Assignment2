# importing libraries
import hashlib
import uuid

# importing other modules
import Latency
import Transaction
import Event
import Node


# class describing a block in the Blockchain
class Block:
    # constructor
    def __init__(self, previous_hash, timestamp, owner, depth):
        self.previous_hash = previous_hash  # hash of the previous/parent block
        self.BlkId = str(uuid.uuid4())  # unique ID of the block
        self.timestamp = timestamp  # timestamp of the creation of block
        self.transactions = []  # list of transactions in the block
        self.balances = []  # list of balances of the nodes after the transactions
        self.owner = owner  # owner/creator/miner of the block
        self.hash = ""  # hash value of the block
        self.size = 0   # number of transactions in the block
        self.depth = depth  # depth of the block in the blockchain, from the genesis block

    # function to calculate the hash of the block
    def calculateHash(self):
        thash = ""
        for txn in self.transactions:
            thash += txn.ID

        self.hash = str(
            hashlib.sha256(
                str(self.previous_hash).encode()
                + str(self.BlkId).encode()
                + str(thash).encode()
            ).hexdigest()
        )

    # function to get the hash of the block
    def getHash(self):
        return self.hash

    # function to add a transaction to the block
    def addTransaction(self, txn):
        self.transactions.append(txn)
        self.size += 1

    # function to get the size of the block
    def getsize(self):
        return self.size

    # function to generate a deepcopy of the block, to prevent Pass by Reference
    def deepCopyBlk(self):
        copyOfBlk = Block(self.previous_hash, self.timestamp, self.owner, self.depth)
        copyOfBlk.previous_hash = self.previous_hash
        copyOfBlk.BlkId = self.BlkId
        copyOfBlk.timestamp = self.timestamp
        copyOfBlk.transactions = []
        copyOfBlk.balances = []
        # deep copy of transactions
        for txn in self.transactions:
            copyOfBlk.transactions.append(txn)
        # deep copy of balances
        for bal in self.balances:
            copyOfBlk.balances.append(bal)
        copyOfBlk.owner = self.owner
        copyOfBlk.hash = self.hash
        copyOfBlk.size = self.size
        copyOfBlk.depth = self.depth
        return copyOfBlk

# class describing the genesis block of the blockchain
class GenesisBlock:
    def __init__(self, timestamp, n):
        self.BlkId = str(1)
        self.timestamp = timestamp
        self.balances = [1000] * n
        self.hash = str(hashlib.sha256((str(self.BlkId).encode())).hexdigest())
        self.depth = 1
        self.owner = "-1"
    
    # function to get the hash of the genesis block
    def getHash(self):
        return self.hash

    # function to generate a deepcopy of the genesis block
    def deepCopyBlk(self):
        copyOfBlk = GenesisBlock(self.timestamp, 0)
        copyOfBlk.BlkId = self.BlkId
        copyOfBlk.timestamp = self.timestamp
        copyOfBlk.balances = []
        # deep copy of balances
        for bal in self.balances:
            copyOfBlk.balances.append(bal)
        copyOfBlk.hash = self.hash
        copyOfBlk.depth = self.depth
        return copyOfBlk


# unit Testing
# def main():
#     ListOfPeers=[]
#     for _ in range(0, 5):
#         ListOfPeers.append(Node.Node(5,0))
#     gen=Block("0",0,1)

#     txn=Transaction.Transaction(ListOfPeers[1].getID(),ListOfPeers[1].getID(),0,ListOfPeers,"coinbase",50)
#     gen.addTransaction(txn)
#     for i in range(10):
#         txn=Transaction.Transaction(ListOfPeers[random.randint(0,4)],ListOfPeers[random.randint(0,4)],i,ListOfPeers,"transfer",random.randint(1,100))

#         gen.addTransaction(txn)
#     genblock=GenesisBlock(0,ListOfPeers)
#     print(genblock.hash)
