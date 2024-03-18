# importing libraries
from PIL import Image
from graphviz import Graph

# importing user modules
import Latency
import Transaction
import Event
import Block
import Blockchain


# function to generate images(graph visualisation) of blockchains for all the nodes, and one merged image
def plotter(ListOfPeers):
    imageFiles = []

    # for each peer, generate an image of the blockchain
    for peer in ListOfPeers:
        edges = set()
        g = Graph(
            "parent",
            filename="graph{}.png".format(peer.idx),
            node_attr={"shape": "box3d", "color": "teal"},
            format="png",
            edge_attr={"dir": "forward", "color": "brown"},
        )
        g.attr(rankdir="LR", splines="line")

        # create nodes for each block in the blockchain
        for key in peer.blockchain.chain:
            if key.BlkId == "1":
                g.node(key.BlkId, label="G")
                continue

            if key.owner == ListOfPeers[0].Id:
                if key in ListOfPeers[0].privateQueue:  # non-broadcasted blocks
                    g.node(
                        key.BlkId,
                        label=str(key.depth),
                        fillcolor="white;0.2:darkseagreen",
                        style="radial",
                    )
                    continue
                else:
                    g.node(
                        key.BlkId,
                        label=str(key.depth),
                        fillcolor="darkseagreen",
                        style="filled",
                    )
                    continue

            if key.owner == ListOfPeers[1].Id:
                if key in ListOfPeers[1].privateQueue:  # non-broadcasted blocks
                    g.node(
                        key.BlkId,
                        label=str(key.depth),
                        fillcolor="white;0.2:gold",
                        style="radial",
                    )
                    continue
                else:
                    g.node(
                        key.BlkId,
                        label=str(key.depth),
                        fillcolor="gold",
                        style="filled",
                    )
                    continue

            g.node(key.BlkId, label=str(key.depth))

        # create edges between the blocks, based on the parent-child relationship
        for key in peer.blockchain.chain:
            for children in peer.blockchain.chain[key]:
                if (key.BlkId, children.BlkId) in edges:
                    continue
                g.edge(key.BlkId, children.BlkId)
                edges.add((key.BlkId, children.BlkId))

        # render the graph and save them as images
        g.render("graphs/" + str(peer.idx), view=False)

        # for generating a merged image of the blockchains
        imageFiles.append("graphs/{}.png".format(peer.idx))
        mergedBlockchains(imageFiles)


# function to generate a merged image of the blockchains
def mergedBlockchains(imageFiles):
    images = [Image.open(x).convert("RGB") for x in imageFiles]
    widths, heights = zip(*(i.size for i in images))
    total_width = max(widths)
    max_height = sum(heights)
    new_im = Image.new("RGB", (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    images = [Image.open(x).convert("RGB") for x in imageFiles]
    widths, heights = zip(*(i.size for i in images))
    total_width = max(widths)
    max_height = sum(heights) + (10 * (len(images) + 2))
    new_im = Image.new("RGB", (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (0, x_offset))
        x_offset += im.size[1]
        x_offset += 10

    new_im.save("graphs/_MergedBlockchain.png")
