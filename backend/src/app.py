import requests
from flask import Flask, request, jsonify
from iparo.IPARO import IPARO
from iparo.IPAROLink import IPAROLink
from iparo.IPFS import IPFS
from io import BytesIO
from warcio.archiveiterator import ArchiveIterator
from warcio.recordloader import ArchiveLoadFailed
import os
import pickle
import hashlib

app = Flask(__name__)
ipfs = IPFS()

IPFS_API_URL = "http://127.0.0.1:5001/api/v0"

def create_iparo(filename=None):
    """Processes WARC file, creates IPARO object with incremented seq_num, pushes to IPFS."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    warc_path = os.path.join(current_dir, '..', 'samples', 'warcs', '2mementos.warc')

    with open(warc_path, 'rb') as stream:
        for record in ArchiveIterator(stream):
            if record.rec_type == 'response':
                url = record.rec_headers.get_header('WARC-Target-URI')
                timestamp = record.rec_headers.get_header('WARC-Date')
                content = record.content_stream().read()

                iparo_object = IPARO(
                    url=url,
                    timestamp=timestamp,
                    seq_num=0,
                    linked_iparos=set(),
                    content=content,
                    nonce=0
                )
                return iparo_object

def add_iparo_to_ipfs(iparo_obj):
    pickled_data = pickle.dumps(iparo_obj)
    response = requests.post(
        f"{IPFS_API_URL}/add",
        files={"file": ("iparo.pkl", pickled_data)}
    )
    print(f"IPFS Hash: {response.json()['Hash']}")
    return response.json()["Hash"]

def update_ipns(cid):
    """Pins an IPFS hash to IPNS using a specific key."""
    response = requests.post(
        f"{IPFS_API_URL}/name/publish",
        params={
            "arg": f"/ipfs/{cid}",
        }
    )
    if response.status_code != 200:
        raise Exception(f"Failed to publish to IPNS: {response.text}")
    
    peer_id = response.json().get("Name", "Unknown IPNS Name")
    print(f" Published to IPNS: /ipns/{peer_id}")
    return peer_id
    
def resolve_ipns_to_cid(peer_id):
    """Resolve IPNS key to the current IPFS hash (CID)."""
    response = requests.post(f"{IPFS_API_URL}/name/resolve", params={"arg": f"/ipns/{peer_id}"})
    if response.status_code != 200:
        raise Exception(f"Failed to resolve IPNS: {response.text}")
    
    path = response.json()["Path"]
    cid = path.split("/")[-1]
    print(f"Resolved IPNS key '{peer_id}' to CID: {cid}")
    return cid

def fetch_iparo_from_ipfs(cid):
    """Fetch and deserialize an IPARO object from IPFS by CID."""
    response = requests.post(f"{IPFS_API_URL}/cat?arg={cid}")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch from IPFS: {response.status_code}")
    iparo = pickle.loads(response.content)
    return iparo

new_iparo = create_iparo()
cid = add_iparo_to_ipfs(new_iparo)
ipns_name = update_ipns(cid)
resolved_cid = resolve_ipns_to_cid(ipns_name)
iparo_from_ipns = fetch_iparo_from_ipfs(resolved_cid)
print(iparo_from_ipns)
print(iparo_from_ipns.__dict__)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
