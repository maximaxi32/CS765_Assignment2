# importing libraries
import uuid
import numpy as np
import random
import copy

# importing other modules
import Latency
import Transaction
import Event
import Block
import Blockchain


# class describing a Peer node in the network
class Node:
    # constructor
    def __init__(self, n, expMean, idx, interArrival):
        self.Id = str(uuid.uuid4()) # unique ID of the node
        self.neighbors = [] # list of neighbors of the node
        self.isSlow = False # boolean to check if the node is slow
        self.isLowCPU = False   # boolean to check if the node has low CPU
        self.toSleep = 1    # time to sleep before generating the next transaction
        self.expMean = expMean  # mean of the exponential distribution for transaction generation delay
        self.txnpool = []   # list of transactions in the transaction pool of this node
        self.verifiedPool = []  # list of verified transactions by this node
        self.idx = idx  # index of the node in the list of peers
        self.hashPower = 0  # hashPower of the node
        self.tkMean = 0 # mean of the exponential distribution for block mining delay
        self.rhos = []  # list of rho values of the node with respect to other nodes
        self.pending = []   # list of pending blocks to be added to the blockchain
        self.invalid = []   # list of invalid blocks received by the node
        self.blockchain = Blockchain.Blockchain(n)  # blockchain of the node
        self.interArrival = interArrival    # interArrival time between two mine block events
        self.minedCnt = 0   # count of the number of blocks mined by the node
        self.receivedCnt = 0    # count of the number of blocks received by the node

    # function to get the ID of the node
    def getID(self):
        return self.Id

    # function to set the isSlow value of the node
    def setSlow(self, isSlow):
        self.isSlow = isSlow

    # function to return the isSlow value of the node
    def getSlow(self):
        return self.isSlow

    # function to set the isLowCPU value of the node
    def setLowCPU(self, isLowCPU):
        self.isLowCPU = isLowCPU

    # function to return the isLowCPU value of the node
    def getLowCPU(self):
        return self.isLowCPU

    # Add one new neighbor to this node
    def addNeighbor(self, newNeighbor):
        self.neighbors.append(newNeighbor)

    # Return a list of node's neighbors
    def getNeighbors(self):
        return self.neighbors

    # function to set the hashPower of the node
    def setHashPower(self, hashPower):
        self.hashPower = hashPower
        self.tkMean = (self.interArrival) / hashPower

    # function to generate a transaction
    def generateTransaction(self, timestamp, ListOfPeers, eventQueue):
        # randomly choosing a peer to send currency to, other than itself
        n = len(ListOfPeers)
        whomToSend = ListOfPeers[random.randint(0, n - 1)]
        indexwhomToSend = self.idx
        while ListOfPeers[indexwhomToSend].getID() == self.Id:
            indexwhomToSend = random.randint(0, n - 1)
            whomToSend = ListOfPeers[indexwhomToSend]

        # randomly choosing the amount to send
        currBalances = self.blockchain.getLastBlock().balances
        whatToSend = np.random.uniform(1, max(1, currBalances[self.idx] / 10))

        # if less than 1 coin is left for the peer, then no transaction should be generated
        if currBalances[self.idx] <= 1:
            with open("TxnLog.txt", "a") as myfile:
                myfile.write("Txn: " + self.Id + " has Insufficient Balance\n")
            return

        # creating the transaction object and adding it to the transaction pool
        Txn = Transaction.Transaction(
            self.Id, whomToSend.getID(), timestamp, ListOfPeers, "transfer", whatToSend
        )
        Txn.printTransaction("transfer")
        self.txnpool.append(Txn)

        # scheduling the next transaction generation event
        self.toSleep = np.random.exponential(self.expMean)
        newtimestamp = timestamp + self.toSleep
        eventQueue.put(
            [
                newtimestamp,
                Event.Event(
                    self,
                    newtimestamp,
                    None,
                    "generateTransaction",
                    ListOfPeers,
                    eventQueue,
                ),
            ]
        )

        # broadcasting the generated transaction to its neighbors
        for neighbor in self.neighbors:
            # network latency based on the size of message to be broadcasted
            newtimestamp = timestamp + Latency.generateLatency(
                ListOfPeers, self.idx, neighbor.idx, 1
            )
            # putting the receive Transaction event for the neighbors in the eventQueue
            eventQueue.put(
                [
                    newtimestamp,
                    Event.Event(
                        neighbor,
                        newtimestamp,
                        Txn,
                        "receiveTransaction",
                        ListOfPeers,
                        eventQueue,
                    ),
                ]
            )

    # function to receive a transaction, sent by another peer
    def receiveTransaction(self, timestamp, Txn, ListOfPeers, eventQueue):
        # if the transaction is already in the pool, then ignore it
        if (Txn in self.txnpool) or (Txn in self.verifiedPool):
            return
        # if the transaction has not been seen before, then add it to your transaction pool
        self.txnpool.append(Txn)

        # broadcasting the received transaction to its neighbors
        for neighbor in self.neighbors:
            # network latency based on the size of message to be broadcasted
            newtimestamp = timestamp + Latency.generateLatency(
                ListOfPeers, self.idx, neighbor.idx, 1
            )
            eventQueue.put(
                [
                    newtimestamp,
                    Event.Event(
                        neighbor,
                        newtimestamp,
                        Txn,
                        "receiveTransaction",
                        ListOfPeers,
                        eventQueue,
                    ),
                ]
            )

    # function to mine a block by a node
    def mineBlock(self, timestamp, prevBlock, ListOfPeers, eventQueue):
        # if the previous block is not the farthest block, then schedule the next mineBlock event on the new longest chain
        if prevBlock.BlkId != self.blockchain.farthestBlock.BlkId:
            # the last block of the new longest chain
            newprevBlock = self.blockchain.getLastBlock()
            nextMine = np.random.exponential(self.tkMean)
            newtimestamp = timestamp + nextMine
            eventQueue.put(
                [
                    newtimestamp,
                    Event.Event(
                        self,
                        newtimestamp,
                        newprevBlock,
                        "mineBlock",
                        ListOfPeers,
                        eventQueue,
                    ),
                ]
            )
            return  # return without mining a block

        # if the transaction pool is empty, then schedule the next mineBlock event, without mining a block now
        if len(self.txnpool) == 0:
            nextMine = np.random.exponential(self.tkMean)
            newtimestamp = timestamp + nextMine
            eventQueue.put(
                [
                    newtimestamp,
                    Event.Event(
                        self,
                        newtimestamp,
                        prevBlock,
                        "mineBlock",
                        ListOfPeers,
                        eventQueue,
                    ),
                ]
            )
            return  # return without mining a block

        # counting the number of blocks mined by the node in total
        self.minedCnt += 1

        # creating a new block to be mined
        newBlock = Block.Block(
            prevBlock.getHash(), timestamp, self.getID(), prevBlock.depth + 1
        )

        # adding coinbase transaction to the new block
        coinbasetxn = Transaction.Transaction(
            self.getID(), self.getID(), timestamp, ListOfPeers, "coinbase", 50
        )
        newBlock.addTransaction(coinbasetxn)
        coinbasetxn.printTransaction("coinbase")

        # create a Deep copy of the balances array from the farthest block in the longest chain
        currBalances = listCopier(prevBlock.balances)
        newBlock.balances = currBalances

        # adding transactions from the transaction pool to the new mined block
        for txn in self.txnpool:
            # add upto 990 KiloBytes of transactions to the block, as block size limit is 1 MegaByte
            if newBlock.size >= 990:
                break

            senderIdx = -1
            receiverIdx = -1
            # To get the indices of sender and receiver, from their IDs
            for peer in ListOfPeers:
                if peer.getID() == txn.sender:
                    senderIdx = peer.idx
                if peer.getID() == txn.receiver:
                    receiverIdx = peer.idx

            # if the sender has enough balance to send the amount, then update the balances and add the transaction to the block
            if currBalances[senderIdx] >= txn.amount:
                currBalances[senderIdx] -= txn.amount
                currBalances[receiverIdx] += txn.amount
                newBlock.balances = currBalances

                # adding the transaction to the block
                newBlock.addTransaction(txn)
                self.txnpool.remove(
                    txn
                )  # remove the transaction from the transaction pool
                self.verifiedPool.append(
                    txn
                )  # add the transaction to the verified transactions pool

        # adding the newly mined block to the blockchain
        newBlock.calculateHash()
        self.blockchain.addBlock(newBlock, self.blockchain.farthestBlock)
        # writing the block to the log file
        with open("blockLogs/Node{}.txt".format(self.idx), "a") as myfile:
            myfile.write(
                "MINED Block with BlkId: {} @ Timestamp: {} by NodeIdx: {}".format(
                    newBlock.BlkId, timestamp, self.idx
                )
                + "\n"
            )

        # updating the longest chain and farthest block, as the new block is on the longest chain
        if newBlock.depth > self.blockchain.longestLength:
            self.blockchain.longestLength = newBlock.depth
            self.blockchain.farthestBlock = newBlock

        # broadcasting the newly mined block to its neighbors, with latency based on block size
        for neighbor in self.neighbors:
            newtimestamp = timestamp + Latency.generateLatency(
                ListOfPeers, self.idx, neighbor.idx, newBlock.size
            )

            # creating a deepcopy of the block to be broadcasted, to prevent pass by reference
            newDeepBlock = newBlock.deepCopyBlk()
            # setting the receiveBlock event for the neighbors in the eventQueue
            eventQueue.put(
                [
                    newtimestamp,
                    Event.Event(
                        neighbor,
                        newtimestamp,
                        newDeepBlock,
                        "receiveBlock",
                        ListOfPeers,
                        eventQueue,
                    ),
                ]
            )

        # adding the event to mine the next block after the intended random delay
        nextMine = np.random.exponential(self.tkMean)
        newtimestamp = timestamp + nextMine
        eventQueue.put(
            [
                newtimestamp,
                Event.Event(
                    self, newtimestamp, newBlock, "mineBlock", ListOfPeers, eventQueue
                ),
            ]
        )

    # function to verify if a block is valid or not
    def verifyBlock(self, block, ListOfPeers):
        # getting balances of every node from the previous block
        parentHash = block.previous_hash
        parentBlock = self.blockchain.getBlock(parentHash)
        curBalances = parentBlock.balances.copy()

        # verifying all the transactions
        for txn in block.transactions:
            if txn.type == "coinbase":
                continue

            # for transfer type transactions
            senderIdx = -1
            receiverIdx = -1
            for peer in ListOfPeers:
                if peer.getID() == txn.sender:
                    senderIdx = peer.idx
                if peer.getID() == txn.receiver:
                    receiverIdx = peer.idx
            if curBalances[senderIdx] >= txn.amount:
                curBalances[senderIdx] -= txn.amount
                curBalances[receiverIdx] += txn.amount
            else:
                # invalid transaction, where sender has insufficient balance
                return False
        return True

    # function to receive a block, sent by another peer
    def receiveBlock(self, timestamp, block, ListOfPeers, eventQueue):
        # if the block is already in the blockchain, then ignore it
        for blk in self.blockchain.chain:
            if blk.BlkId == block.BlkId:
                return

        # check if parent block exists in the blockchain, if not, put the block in the list of pending blocks
        parentblock = self.blockchain.getBlock(block.previous_hash)
        if parentblock == None:
            if block in self.pending:
                return
            self.pending.append(block)
            return

        # make a deep copy of block to prevent pass by reference
        copyOfBlk = block.deepCopyBlk()

        # if the block is invalid, then put it in the list of invalid blocks
        if not self.verifyBlock(copyOfBlk, ListOfPeers):
            # print("verification failed " + self.Id)
            self.invalid.append(copyOfBlk)
            return

        # ensure that the transactions in the block are not in the transaction pool and verified pool
        txnpoolCopy = listCopier(self.txnpool)
        verifiedPoolCopy = listCopier(self.verifiedPool)
        for txn in copyOfBlk.transactions:
            if txn in verifiedPoolCopy:
                pass
            else:
                verifiedPoolCopy.append(txn)
            if txn in txnpoolCopy:
                txnpoolCopy.remove(txn)
        self.txnpool = txnpoolCopy
        self.verifiedPool = verifiedPoolCopy

        # to count the number of blocks received by the node
        self.receivedCnt += 1

        # if the received block makes a new longest chain, then update the longest length and farthest block
        copyOfBlk.depth = parentblock.depth + 1
        if copyOfBlk.depth > self.blockchain.longestLength:
            self.blockchain.longestLength = copyOfBlk.depth
            self.blockchain.farthestBlock = copyOfBlk

        # adding the block to the blockchain
        self.blockchain.addBlock(copyOfBlk, parentblock)
        # writing the block to the log file
        with open("blockLogs/Node{}.txt".format(self.idx), "a") as myfile:
            myfile.write(
                "RECEIVED Block with BlkId: {} @ Timestamp: {} by NodeIdx: {}".format(
                    copyOfBlk.BlkId, timestamp, self.idx
                )
                + "\n"
            )

        # check recursively if children of the received block exist in pending
        stillsearching = True
        while stillsearching == True and len(self.pending) > 0:
            stillsearching = False
            for blk in self.pending:
                for currBlock in self.blockchain.chain:
                    if blk.previous_hash == currBlock.getHash():
                        # if the received block is a parent of one of the pending blocks, add it to the blockchain
                        self.pending.remove(blk)
                        self.blockchain.addBlock(blk, currBlock)
                        # writing the block to the log file
                        with open(
                            "blockLogs/Node{}.txt".format(self.idx), "a"
                        ) as myfile:
                            myfile.write(
                                "RECEIVED Block with BlkId: {} @ Timestamp: {} by NodeIdx: {}".format(
                                    blk.BlkId, timestamp, self.idx
                                )
                                + "\n"
                            )

                        # updating the longest chain and farthest block if the new block is on the longest chain
                        blk.depth = currBlock.depth + 1
                        if blk.depth > self.blockchain.longestLength:
                            self.blockchain.longestLength = blk.depth
                            self.blockchain.farthestBlock = blk

                        # broadcasting the receive block event to the neighbors, for one of the pending blocks
                        for neighbor in self.neighbors:
                            newtimestamp = timestamp + Latency.generateLatency(
                                ListOfPeers, self.idx, neighbor.idx, blk.size
                            )
                            eventQueue.put(
                                [
                                    newtimestamp,
                                    Event.Event(
                                        neighbor,
                                        newtimestamp,
                                        blk.deepCopyBlk(),
                                        "receiveBlock",
                                        ListOfPeers,
                                        eventQueue,
                                    ),
                                ]
                            )
                        # to check if some chain is being formed by the pending blocks
                        stillsearching = True
                        break

        # broadcasting the block to neighbors, with some latency based on the size of the block
        for neighbor in self.neighbors:
            newtimestamp = timestamp + Latency.generateLatency(
                ListOfPeers, self.idx, neighbor.idx, copyOfBlk.size
            )
            eventQueue.put(
                [
                    newtimestamp,
                    Event.Event(
                        neighbor,
                        newtimestamp,
                        copyOfBlk,
                        "receiveBlock",
                        ListOfPeers,
                        eventQueue,
                    ),
                ]
            )

    # function to get the number of blocks mined by the node in its longest chain
    def cntInLongest(self):
        cnt=0
        if self.blockchain.farthestBlock.owner==self.Id:
            cnt+=1
        prev_hash=self.blockchain.farthestBlock.previous_hash
        # iteratively travelling back the blockchain from farthest block to genesis block
        while prev_hash!=self.blockchain.genesisBlock.hash:
            for blk in self.blockchain.chain:
                if blk.getHash()==prev_hash:
                    if blk.owner==self.Id:
                        cnt+=1
                    prev_hash=blk.previous_hash
                    break
        return cnt

# function to generate a deepcopy of a list
def listCopier(lst):
    copylst = []
    for i in lst:
        copylst.append(i)
    return copylst
