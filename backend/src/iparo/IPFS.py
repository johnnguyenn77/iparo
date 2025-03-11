import hashlib
import pickle
from datetime import datetime
from enum import Enum
from typing import Optional

from iparo.IPARO import IPARO
from iparo.IPARODateConverter import IPARODateConverter
from iparo.IPNS import ipns


class Mode(Enum):
    LATEST_BEFORE = 0,
    CLOSEST = 1,
    EARLIEST_AFTER = 2


class IPFS:
    """
    The InterPlanetary File System is responsible for hashing, storing,
    retrieving, and linking IPARO objects.
    """

    def __init__(self):
        self.data: dict[str, bytes] = {}
        self.retrieve_count = 0
        self.store_count = 0

    def store(self, iparo: IPARO) -> str:
        """
        Stores a node with its CID.

        Args:
            iparo (IPARO): The IPARO object to store.

        Returns:
            The CID of the newly stored IPARO.
        """
        iparo_bytes = pickle.dumps(iparo)
        sha256_hash = hashlib.sha256(iparo_bytes).hexdigest()
        cid = 'Qm' + sha256_hash[:34]
        self.store_count += 1
        self.data[cid] = iparo_bytes
        return cid

    def reset_data(self):
        self.data: dict[str, IPARO] = {}

    def retrieve(self, cid) -> Optional[IPARO]:
        """
        Retrieves the IPARO object corresponding to a given CID, if it exists, otherwise, ``None``.
        """
        self.retrieve_count += 1
        iparo_bytes = self.data.get(cid)
        return pickle.loads(iparo_bytes) if iparo_bytes is not None else iparo_bytes

    def retrieve_by_timestamp(self, url: str, target_timestamp: datetime, mode: Mode = Mode.LATEST_BEFORE) -> \
            Optional[str]:
        """
        Retrieves the IPARO versions of a given URL closest to a given datetime if at least one
        IPARO version is stored in the IPFS, otherwise ``None``. Default is the latest timestamp
        that occurs before the target timestamp, but ``Mode.EARLIEST_AFTER`` gives the node with
        the earliest time after a given timestamp, and ``Mode.CLOSEST`` gives the node with the
        closest timestamp to a given timestamp. If the distance from the two closest times to
        the target timestamp are equal, the CID with the earlier sequence number will be chosen.
        """
        self.retrieve_count += 1
        latest_cid = ipns.get_latest_cid(url)
        latest_node = self.retrieve(latest_cid)
        # Note: the only times that the "earliest after" mode returns None are when:
        # 1. there are no nodes to begin with.
        # 2. the target timestamp comes after the latest time.

        # The first case is tackled by an if statement
        if latest_node is None:
            return None
        latest_time = IPARODateConverter.str_to_datetime(latest_node.timestamp)

        # The second case is tackled by another if statement. Of course,
        # when the target timestamp comes after the latest time (on any other mode),
        # the latest CID gets chosen.
        if target_timestamp > latest_time and mode == Mode.EARLIEST_AFTER:
            return None
        elif target_timestamp > latest_time:
            return latest_cid

        # Find the earliest node after a given timestamp
        cid = latest_cid
        node = latest_node
        while IPARODateConverter.str_to_datetime(node.timestamp) > target_timestamp:
            linked_iparos = node.linked_iparos
            # Find earliest node after the target timestamp
            next_cid = None
            next_timestamp = None

            # Traverse through all links to find the next CID and timestamp
            for link in linked_iparos:
                curr_timestamp = IPARODateConverter.str_to_datetime(link.timestamp)

                is_relevant = curr_timestamp >= target_timestamp
                is_closest = next_timestamp is None or curr_timestamp <= next_timestamp

                if is_relevant and is_closest:
                    next_cid = link.cid
                    next_timestamp = IPARODateConverter.str_to_datetime(link.timestamp)

            if next_cid is None:
                break

            cid = next_cid
            node = self.retrieve(cid)

        # Get closest timestamp
        node_timestamp = IPARODateConverter.str_to_datetime(node.timestamp)

        # Case 1: Target timestamp is equal to node timestamp. In this case, we can just return the CID.
        # Case 2: Mode == Earliest after, in which case returning the CID should be sufficient.
        if node_timestamp == target_timestamp or mode == Mode.EARLIEST_AFTER:
            return cid

        # Case 3: Sequence number is 0 and mode is latest before. Returns None.
        if node.seq_num == 0 and mode == Mode.LATEST_BEFORE:
            return None

        # Case 4: The node is the very first node and the mode is not "latest before".
        # This will return the CID of the first IPARO.
        elif node.seq_num == 0:
            return cid

        # Find previous node - assume that can never be None
        before_node = [link for link in node.linked_iparos if link.seq_num == node.seq_num - 1][0]
        if mode == Mode.LATEST_BEFORE:
            return before_node.cid

        before_node_timestamp = IPARODateConverter.str_to_datetime(before_node.timestamp)

        # r measures how close to the "before node" the target timestamp is, as a percentage of
        # the total time gap between the two consecutive nodes.
        r = (target_timestamp - before_node_timestamp) / (node_timestamp - before_node_timestamp)
        return before_node.cid if r <= 0.5 else cid

    def retrieve_by_number(self, url: str, number: int) -> Optional[str]:
        """
        Retrieves the IPARO CID corresponding to a given sequence number and a URL.
        """
        cid = ipns.get_latest_cid(url)
        if cid is None:
            return None
        cids = [cid]
        while True:
            iparo = self.retrieve(cid)
            if iparo.seq_num == number:
                return cid
            # TODO: Optimize
            link = min((link for link in iparo.linked_iparos if link.seq_num >= number),
                       default=None, key=lambda x: x.seq_num)
            if link is None or link.seq_num == number:
                break
            cid = link.cid
            cids.append(cid)

        return link.cid if link is not None else None

    def get_counts(self) -> dict:
        """
        Returns the number of store, and retrieve operations performed.

        Returns:
            dict: Dictionary with counts of store, and retrieve operations.
        """
        counts = {"store": self.store_count, "retrieve": self.retrieve_count}
        return counts

    def reset_counts(self):
        """
        Resets the operation counters.
        """
        self.store_count = 0
        self.retrieve_count = 0

    def get_all_cids(self, url: str) -> list[str]:
        """
        Retrieves the list of all CIDs in the IPFS, corresponding to the given URL.
        The nodes are sorted from latest to earliest.
        """
        cid = ipns.get_latest_cid(url)
        if cid is None:
            return []
        cids = [cid]
        while True:
            iparo = self.retrieve(cid)
            # TODO: Optimize
            links = [link for link in iparo.linked_iparos if link.seq_num == iparo.seq_num - 1]
            if len(links) == 0:
                break
            cid = links[0].cid
            cids.append(cid)

        return cids


ipfs = IPFS()
