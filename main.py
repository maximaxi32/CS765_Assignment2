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
# usage: main.py [-h] --n N --z0 Z0 --z1 Z1 --Tx TX --Itr ITR --Sim SIM
def main():
    # Declaring user arguments
    parser.add_argument("--n", type=int, required=True)  # number of Nodes
    parser.add_argument("--z0", type=float, required=True)  # percentage of slow nodes
    parser.add_argument(
        "--z1", type=float, required=True
    )  # percentage of low CPU nodes
    parser.add_argument(
        "--Tx", type=float, required=True
    )  # mean time for interarrival between two generated Transactions in seconds
    parser.add_argument(
        "--Itr", type=float, required=True
    )  # mean time for interarrival between two mined Blocks in seconds
    parser.add_argument(
        "--Sim", type=float, required=True
    )  # Total simulation time in seconds

    # Parsing the arguments
    args = parser.parse_args()
    n = args.n
    z0 = args.z0
    z1 = args.z1
    Tx = args.Tx
    Itr = args.Itr
    timeLimit = args.Sim

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
        newNode = Node.Node(n, Tx, _, Itr)
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
    assign_z0(ListOfPeers, z0, n)
    assign_z1(ListOfPeers, z1, n)

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

    # Saving the blockchain as images for all the peers
    Graph.plotter(ListOfPeers)

    # Printing the stats for all peers after simulation completes
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    totalMined = 0
    for peer in range(n):
        print(
            "Stats for Node {} having isSlow={} and isLowCPU={}".format(
                ListOfPeers[peer].idx,
                ListOfPeers[peer].isSlow,
                ListOfPeers[peer].isLowCPU,
            )
        )
        print("Number of Blocks mined:", ListOfPeers[peer].minedCnt, end=" || ")
        print("Number of Blocks received:", ListOfPeers[peer].receivedCnt)
        print(
            "Length of longest chain in Blockchain:",
            ListOfPeers[peer].blockchain.farthestBlock.depth,
        )
        totalMined += ListOfPeers[peer].minedCnt
        print("Ratio of Blocks mined on the longest chain : Total Blocks Mined = {} : {} ". format(ListOfPeers[peer].cntInLongest(), ListOfPeers[peer].minedCnt))
        print(
            "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        )
    print("Number of Generate Transaction Events: " + str(genTxn))
    print("Total number of Blocks Mined:", totalMined)


# Function to assign isSlow values to the Nodes randomly
def assign_z0(ListOfPeers, z0, n):
    numTrues = int((z0 * n) / 100)
    labels = [True] * numTrues
    labelsFalse = [False] * (n - numTrues)
    labels += labelsFalse
    random.shuffle(labels)
    for _ in range(n):
        ListOfPeers[_].setSlow(labels[_])


# Function to assign isLowCPU values to the Nodes randomly
def assign_z1(ListOfPeers, z1, n):
    # hashPowerofLow * n * z1 + hashPowerofHigh * (n - (n * z1) = 1

    numTrues = int((z1 * n) / 100)
    labels = [True] * numTrues
    hashPowerofLow = 1 * 100 / (10 * n - 9 * numTrues)
    hashPowerofHigh = 10 * hashPowerofLow

    labelsFalse = [False] * (n - numTrues)
    labels += labelsFalse
    random.shuffle(labels)
    for _ in range(n):
        ListOfPeers[_].setLowCPU(labels[_])
        if labels[_] == True:
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


# calling the main function
if __name__ == "__main__":
    main()
