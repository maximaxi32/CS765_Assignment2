# NOTE: The seconds used in simulation are "simulated seconds" and not real-life seconds of time

# importing libraries
import argparse
import random
from queue import PriorityQueue
import numpy as np
import os

# importing user modules
import Node
import Network
import Event
import Graph


# matrix to store the rho values between every pair of nodes
# Rho = speed of light propogation delay
rhoMatrix = []

# setting up the input arguments parser
parser = argparse.ArgumentParser()


# This is the main function
# usage: python3 main.py [-h] --n N --Tx TX --Itr ITR --Sim SIM --Zeta1 ZETA1 --Zeta2 ZETA2
def main():

    # Declaring user arguments
    parser.add_argument("--n", type=int, required=True)  # number of Nodes
    # parser.add_argument("--z0", type=float, required=True)  # percentage of slow nodes
    # parser.add_argument("--z1", type=float, required=True)  # percentage of low CPU nodes
    parser.add_argument(
        "--Tx", type=float, required=True
    )  # mean time for interarrival between two generated Transactions in seconds
    parser.add_argument(
        "--Itr", type=float, required=True
    )  # mean time for interarrival between two mined Blocks in seconds
    parser.add_argument(
        "--Sim", type=float, required=True
    )  # Total simulation time in seconds
    parser.add_argument(
        "--Zeta1", type=float, required=True
    )  # Hash power of Adversary 1, given in percentage
    parser.add_argument(
        "--Zeta2", type=float, required=True
    )  # Hash power of Adversary 2, given in percentage

    # Parsing the arguments
    args = parser.parse_args()
    n = args.n
    # z0 = args.z0
    # z1 = args.z1
    Tx = args.Tx
    Itr = args.Itr
    timeLimit = args.Sim
    zeta1 = args.Zeta1
    zeta2 = args.Zeta2

    eventQueue = (
        PriorityQueue()
    )  # Global Event Queue implemented with a min Priority Queue

    # Creating and Clearing the Log Files
    directory = "blockLogs"
    if not os.path.isdir(directory):
        os.mkdir(directory)
    for file in os.listdir(directory):
        os.remove("blockLogs/" + file)
    for f in range(n):
        open("blockLogs/Node" + str(f) + ".txt", "w").close()

    open("TxnLog.txt", "w").close()

    # Initializing the list of peer nodes
    ListOfPeers = []
    for _ in range(0, n):
        if _ == 0 or _ == 1:
            newNode = Node.Node(n, Tx, _, Itr, True)
        else:
            newNode = Node.Node(n, Tx, _, Itr, False)

        ListOfPeers.append(newNode)
        newNode.rhos = [0] * n
        firstTxn = np.random.exponential(Tx)
        # Generating the first generateTransaction event for each Node
        eventQueue.put(
            [
                firstTxn,
                Event.Event(
                    newNode,
                    firstTxn,
                    None,
                    "generateTransaction",
                    ListOfPeers,
                    eventQueue,
                ),
            ]
        )

    # Assigning isSlow and isLowCPU values to the Nodes
    assign_z0(ListOfPeers, n)
    assign_z1(ListOfPeers, n)

    # Generating the first mineBlock event for each Node
    for peer in ListOfPeers:
        firstMine = np.random.exponential(Itr / peer.hashPower) / 2
        eventQueue.put(
            [
                firstMine,
                Event.Event(
                    peer,
                    firstMine,
                    peer.blockchain.genesisBlock,
                    "mineBlock",
                    ListOfPeers,
                    eventQueue,
                ),
            ]
        )

    # Create Network of peers
    Network.createNetwork(ListOfPeers)

    # create rho matrix and assign Rho values to the pair of Nodes
    rhoGenerator(ListOfPeers)

    genTxn = 0  # To keep track of number of generate Transaction events

    # Loop to simulate and execute events from eventqueue
    while 1:
        currEvent = eventQueue.get()[1]
        # simulating the events till the timeLimit
        if currEvent.timestamp > timeLimit:
            break
        if currEvent.eventType == "generateTransaction":
            genTxn += 1
        currEvent.execute(ListOfPeers, eventQueue)

    # After simulation completes, adding the remaining privateQueue blocks to the blockchain
    for block in ListOfPeers[0].privateQueue:
        ListOfPeers[0].blockchain.addBlock(
            block, ListOfPeers[0].blockchain.farthestBlock
        )
        ListOfPeers[0].blockchain.farthestBlock = block
        ListOfPeers[0].blockchain.longestLength = block.depth
    for block in ListOfPeers[1].privateQueue:
        ListOfPeers[1].blockchain.addBlock(
            block, ListOfPeers[1].blockchain.farthestBlock
        )
        ListOfPeers[1].blockchain.farthestBlock = block
        ListOfPeers[1].blockchain.longestLength = block.depth

    # Saving the blockchain as images for all the peers
    Graph.plotter(ListOfPeers)

    # Printing the stats for all peers after simulation completes

    totalMined = 0
    for peer in range(n):
        print(
            "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        )
        print(
            "Stats for Node {} having isSlow={} and isLowCPU={}".format(
                ListOfPeers[peer].idx,
                ListOfPeers[peer].isSlow,
                ListOfPeers[peer].isLowCPU,
            )
        )
        """
        Was displayed in assignment 1, but not in assignment 2
        print("Number of Blocks mined:", ListOfPeers[peer].minedCnt, end=" || ")
        print("Number of Blocks received:", ListOfPeers[peer].receivedCnt)
        """

        print(
            "Length of longest chain in Blockchain:",
            ListOfPeers[peer].blockchain.farthestBlock.depth,
        )
        totalMined += ListOfPeers[peer].minedCnt
        print(
            "Ratio of Blocks mined on the longest chain : Total Blocks Mined = {} : {} ".format(
                ListOfPeers[peer].cntInLongest(), ListOfPeers[peer].minedCnt
            )
        )

    # printing one-time stats at the end of the simulation
    print("===========================================================================")
    print("Number of Generate Transaction Events: " + str(genTxn))
    print("Total number of Blocks Mined:", totalMined)
    """
    Added for assignment 2
    """
    # MPU Node Adversary = Number of block mined by an adversary in final public main chain / Total number of blocks mined by this adversary overall
    mpu1 = mpuCalculatorAdv(ListOfPeers, 0)
    mpu2 = mpuCalculatorAdv(ListOfPeers, 1)
    print("MPU Node Adversary 1:", mpu1)
    print("MPU Node Adversary 2:", mpu2)
    # MPU Node Overall = Number of block in the final public main chain / Total number of blocks generated across all the nodes
    print(
        "MPU Node Overall:",
        round(ListOfPeers[2].blockchain.farthestBlock.depth / totalMined, 4),
    )
    print("===========================================================================")


# Function to assign isSlow values to the Nodes randomly
def assign_z0(ListOfPeers, n):
    ListOfPeers[0].setSlow(False)
    ListOfPeers[1].setSlow(False)

    # Assigning fast and slow nodes to other nodes
    N = n - 2
    z0 = 50  # Assignment 2: half of all the honest nodes are slow
    numTrues = int((z0 * N) / 100)
    labels = [True] * numTrues
    labelsFalse = [False] * (N - numTrues)
    labels += labelsFalse
    random.shuffle(labels)
    for _ in range(2, n):
        ListOfPeers[_].setSlow(labels[_ - 2])


# Function to assign isLowCPU values to the Nodes randomly
def assign_z1(ListOfPeers, n):
    args = parser.parse_args()
    # Handling zero hashpower input case for adversaries
    if args.Zeta1 == 0:
        args.Zeta1 = 0.0000001
    if args.Zeta2 == 0:
        args.Zeta2 = 0.0000001

    ListOfPeers[0].setHashPower(args.Zeta1 / 100)
    ListOfPeers[1].setHashPower(args.Zeta2 / 100)

    N = n - 2
    z1 = 0  # Assignment 2: All honest miners have equal hashing power, so repurposed the function to make all honest nodes same

    # hashPowerofLow * n * z1 + hashPowerofHigh * (n - (n * z1) + pow(0) + pow(1) = 1
    numTrues = int((z1 * N) / 100)
    labels = [True] * numTrues
    hashPowerofLow = (1) * (100 - args.Zeta1 - args.Zeta2) / (10 * N - 9 * numTrues)
    hashPowerofHigh = 10 * hashPowerofLow

    labelsFalse = [False] * (N - numTrues)
    labels += labelsFalse
    random.shuffle(labels)
    for _ in range(2, n):
        ListOfPeers[_].setLowCPU(labels[_ - 2])
        if labels[_ - 2] == True:
            ListOfPeers[_].setHashPower(hashPowerofLow / 100)
        else:
            ListOfPeers[_].setHashPower(hashPowerofHigh / 100)


# function to generate Rho values between every pair of nodes
def rhoGenerator(ListOfPeers):
    n = len(ListOfPeers)  # number of Nodes in network
    for i in range(n):
        for j in range(i):
            currentRho = np.random.uniform(0.01, 0.5)
            ListOfPeers[i].rhos[ListOfPeers[j].idx] = currentRho
            ListOfPeers[j].rhos[ListOfPeers[i].idx] = currentRho


"""
Assignment-2 functions added
"""


# Calculates mpu value for an adversary w.r.t Honest Node 1 (Node having idx = 2)
def mpuCalculatorAdv(ListOfPeers, advIdx):
    cnt = 0
    honest = ListOfPeers[2]
    adversary = ListOfPeers[advIdx]

    # if adversary has not mined any block then the ratio is undefined
    if adversary.minedCnt == 0:
        return "No Blocks Mined by Adversary"

    if honest.blockchain.farthestBlock.owner == adversary.Id:
        cnt += 1
    prev_hash = honest.blockchain.farthestBlock.previous_hash
    # iteratively travelling back the blockchain from farthest block to genesis block
    while prev_hash != honest.blockchain.genesisBlock.hash:
        for blk in honest.blockchain.chain:
            if blk.getHash() == prev_hash:
                if blk.owner == adversary.Id:
                    cnt += 1
                prev_hash = blk.previous_hash
                break
    # returning MPU Adversary ratio
    return round(cnt / adversary.minedCnt, 4)


# calling the main function
if __name__ == "__main__":
    main()
