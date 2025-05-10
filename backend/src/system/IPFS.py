import pickle

import requests

from system.IPARO import IPARO
from system.IPAROException import IPARONotFoundException
from system.IPAROLink import IPAROLink
from system.Utils import Utils
from simulation.IPFS import Mode
from datetime import datetime



class IPFS:
    def store(self, iparo_obj: IPARO):
        pickled_data = pickle.dumps(iparo_obj)
        response = requests.post(
            f"{Utils.IPFS_API_URL}/add",
            files={"file": ("iparo.pkl", pickled_data)}
        )
        print(f"IPFS Hash: {response.json()['Hash']}")
        return response.json()["Hash"]

    def retrieve(self, cid: str) -> IPARO:
        """Fetch and deserialize an IPARO object from IPFS by CID."""
        response = requests.post(f"{Utils.IPFS_API_URL}/cat?arg={cid}")
        if response.status_code != 200:
            raise Exception(f"Failed to fetch from IPFS: {response.status_code}")
        iparo = pickle.loads(response.content)
        return iparo

    def retrieve_by_number(self, latest_link: IPAROLink, num: int):
        """Fetch an IPARO with the desired sequence number, using a link to the latest node."""
        curr_link = latest_link
        if num < 0 or num > latest_link.seq_num:
            raise IPARONotFoundException("Invalid sequence number: " + str(num))
        while curr_link.seq_num > num:
            iparo = self.retrieve(curr_link.cid)
            curr_link = min([linked_iparo for linked_iparo in iparo.linked_iparos if linked_iparo.seq_num >= num],
                            key=lambda link: link.seq_num)

        return curr_link

    def retrieve_by_date(self, latest_link: IPAROLink, target_timestamp: str, mode: Mode):
        """Fetch an IPARO with the closest timestamp, using a link to the latest node. For
        the closest timestamp, if the target timestamp is exactly halfway between the current
        timestamp and the previous timestamp, then the method will return the current link."""
        # Scenario 1: Current link timestamp <= target timestamp
        # Scenario 2: There is no previous node.
        if latest_link.timestamp <= target_timestamp or latest_link.seq_num == 0:
            return latest_link

        # Otherwise, we assume that a previous node exists and target timestamp < current timestamp.
        curr_link = latest_link
        iparo = self.retrieve(latest_link.cid)

        # First, we filter, and then we find the previous link.
        candidate_links = {link for link in iparo.linked_iparos if link.timestamp >= target_timestamp}
        known_links = candidate_links
        prev_link = max(candidate_links, key=lambda link: link.seq_num)
        known_links.add(curr_link)

        # Post-loop invariant: prev_link.timestamp <= target_timestamp
        # Loop invariant: target_timestamp <= curr_link.timestamp
        while prev_link.timestamp > target_timestamp:
            # Now we update
            curr_link = min(known_links, key=lambda link: (link.timestamp, link.seq_num))
            if curr_link.seq_num == 0 and curr_link.timestamp > target_timestamp:
                return curr_link  # No way to get closer than current link at this point.

            iparo = self.retrieve(curr_link.cid)
            
            # To test prev_link condition.
            candidate_links = {link for link in iparo.linked_iparos if link.timestamp >= target_timestamp}
            known_links.update(candidate_links)
            prev_link = max(candidate_links, key=lambda link: link.seq_num)

        curr_ts = datetime.fromisoformat(latest_link.timestamp)
        prev_ts = datetime.fromisoformat(prev_link.timestamp)
        target_ts = datetime.fromisoformat(target_timestamp)

        # Scenario 3: prev_ts == curr_ts (causing div by 0)
        if prev_ts == curr_ts:
            return curr_link

        # Scenario 4: prev_ts < curr_ts
        # Calculate ratio to see if it's closer or not.
        r = (target_ts - curr_ts) / (curr_ts - prev_ts)
        if mode == Mode.CLOSEST:
            return prev_link if r < 0.5 else curr_link
        elif mode == Mode.LATEST_BEFORE:
            return prev_link if r < 1 else curr_link
        # else (mode == Mode.EARLIEST_AFTER):
        return prev_link if r == 0 else curr_link
