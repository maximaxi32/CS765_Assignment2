# importing libraries
import random
import networkx as nx
import matplotlib.pyplot as plt
import os 

# importing user modules
import Node


# function to create a P2P network of Peer Nodes
def createNetwork(ListofPeers):
    if len(ListofPeers) < 4:
        print("Could not generate a connected network, take a different N")
        exit(0)

    # To ensure finite number of attempts to create a connected network
    attempts = 0

    while attempts < 100:
        attempts += 1
        print("Attempting to generate a network ... ")
        # generate a new P2P network, within the given constraints
        for _ in range(0, len(ListofPeers)):
            numOfNeighbors = random.randint(3, min(len(ListofPeers) - 1, 6)) - len(
                ListofPeers[_].getNeighbors()
            )
            if numOfNeighbors <= 0:
                continue

            attempts2 = 0
            while numOfNeighbors > 0:
                newNeighborIdx = random.randint(0, len(ListofPeers) - 1)
                # print(str(_) + " --> " + str(newNeighborIdx))

                newNeighbor = ListofPeers[newNeighborIdx]
                if (
                    (newNeighbor not in ListofPeers[_].getNeighbors())
                    and (newNeighbor.getID() != ListofPeers[_].getID())
                    and (len(newNeighbor.getNeighbors()) < 6)
                ):
                    # Adding bidirectional edges for the neighbors
                    ListofPeers[_].addNeighbor(newNeighbor)
                    newNeighbor.addNeighbor(ListofPeers[_])
                    numOfNeighbors -= 1

                attempts2 += 1
                if attempts2 > len(ListofPeers) * 10:
                    break

        # check if the generated P2P network is connected or not
        if isConnected(ListofPeers) == True:
            print("Generated a connected network!")
            createGraph(ListofPeers)
            return

        elif attempts > 100:
            print("Could not generate a connected network, take a different N")
            exit(0)

        for _ in range(0, len(ListofPeers)):
            ListofPeers[_].neighbors = []

        # If the generated network is disconnected, retry
        print("Issue: Generated network is disconnected. Retrying...")

        # rhoGenerator(ListofPeers)
        # print(rhoMatrix)


# function to create the image of the network topology graph
def createGraph(ListOfPeers):
    n = len(ListOfPeers)
    adj = dict()
    for i in range(n):
        adj[ListOfPeers[i]] = ListOfPeers[i].getNeighbors()

    # Saving the topology to an image
    G = nx.Graph(adj)

    pos = nx.spring_layout(G)
    nx.draw(
        G,
        pos,
        with_labels=False,
        node_color="red",
        node_size=50,
        font_size=8,
        font_weight="bold",
    )

    # Save the graph as a png file
    directory = "graphs"
    if not os.path.isdir(directory):
        os.mkdir(directory)
    plt.savefig("graphs/_Topology.png")
    plt.clf()


# function to check if the network is a connected graph or not
def isConnected(ListOfPeers):
    if not ListOfPeers:
        return True
    visited = set()
    start_node = ListOfPeers[0]
    dfs(start_node, visited)
    # true if all the nodes have been visited
    return len(visited) == len(ListOfPeers)


# using Depth First Search on the network topology
def dfs(node, visited):
    visited.add(node)
    currNeighbors = node.getNeighbors()
    for neighbor in currNeighbors:
        if neighbor not in visited:
            dfs(neighbor, visited)
