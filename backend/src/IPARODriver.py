import random
import time

from IPAROFactory import IPAROFactory
from IPFS import ipfs
from LinkingStrategy import SequentialExponentialStrategy
from IPNS import ipns


if __name__ == '__main__':
    url = "example.com"
    node_num = 50
    strategy = SequentialExponentialStrategy(2)


    # Reset the operation counts
    ipns.reset_counts()
    ipfs.reset_counts()

    # Pick a random node to search for
    node_num = random.randint(0, node_num - 1)
    print(f"Looking for node with sequence number: {node_num}")

    # Traverse back through the linked nodes to find the target
    # Output the found node
    if cid is not None:
        node = ipfs.retrieve(cid)
        print(f"Node found with contents: {node.content}")
    else:
        print("Can't find node")
