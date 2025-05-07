import pickle

import requests

from system.Utils import Utils
from system.IPARO import IPARO
from system.IPAROLink import IPAROLink
from system.IPNS import IPNS

class IPFS:
    def store(self, iparo_obj):
        pickled_data = pickle.dumps(iparo_obj)
        response = requests.post(
            f"{Utils.IPFS_API_URL}/add",
            files={"file": ("iparo.pkl", pickled_data)}
        )
        print(f"IPFS Hash: {response.json()['Hash']}")
        return response.json()["Hash"]

    def retrieve(self, cid):
        """Fetch and deserialize an IPARO object from IPFS by CID."""
        response = requests.post(f"{Utils.IPFS_API_URL}/cat?arg={cid}")
        if response.status_code != 200:
            raise Exception(f"Failed to fetch from IPFS: {response.status_code}")
        iparo = pickle.loads(response.content)
        return iparo