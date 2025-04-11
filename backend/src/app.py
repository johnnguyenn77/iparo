import requests
from flask import Flask, request, jsonify
from iparo.IPARO import IPARO
from io import BytesIO
from warcio.archiveiterator import ArchiveIterator
from warcio.recordloader import ArchiveLoadFailed
import os
import pickle
import hashlib

app = Flask(__name__)

IPFS_API_URL = "http://127.0.0.1:5001/api/v0"


def create_iparo(filename=None):
    """Processes WARC file, creates IPARO objects, and pushes them to IPFS and IPNS."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    warc_path = os.path.join(current_dir, '..', 'samples', 'warcs', '1memento_noContentType.warc')
    
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
            
            
def generate_key_for_url(url):
    url_hash = hashlib.sha256(url.encode()).hexdigest()
    key_name = f"urlkey-{url_hash[:10]}"

    # Check if key already exists
    existing_keys = requests.post("http://127.0.0.1:5001/api/v0/key/list").json()
    if key_name not in [k["Name"] for k in existing_keys["Keys"]]:
        res = requests.post("http://127.0.0.1:5001/api/v0/key/gen", params={
            "arg": key_name,
            "type": "rsa",
            "size": "2048"
        })
        print(f"Generated new key: {key_name}")
    else:
        print(f"Using existing key: {key_name}")

    return key_name

def get_ipns_name_for_key(key_name):
    """Returns the IPNS name (PeerID) for a given key."""
    response = requests.post("http://127.0.0.1:5001/api/v0/key/list").json()
    for key in response["Keys"]:
        if key["Name"] == key_name:
            return key["Id"]
    raise Exception(f"Key '{key_name}' not found.")

def add_iparo_to_ipfs(iparo_obj):
    pickled_data = pickle.dumps(iparo_obj)
    response = requests.post(
        f"{IPFS_API_URL}/add",
        files={"file": ("iparo.pkl", pickled_data)}
    )
    print("Succesfully add to ipfs")
    print(f"IPFS Hash: {response.json()['Hash']}")
    return response.json()["Hash"]

def update_ipns(ipfs_hash, key_name):
    """Pins an IPFS hash to IPNS using a specific key."""
    response = requests.post(
        f"{IPFS_API_URL}/name/publish",
        params={
            "arg": f"/ipfs/{ipfs_hash}",
            "key": key_name
        }
    )
    if response.status_code != 200:
        raise Exception(f"Failed to publish to IPNS: {response.text}")
    
    ipns_name = response.json().get("Name", "Unknown IPNS Name")
    print(f" Published to IPNS with key '{key_name}': /ipns/{ipns_name}")
    return ipns_name
    
def resolve_ipns_to_cid(key_name):
    """Resolve IPNS key to the current IPFS hash (CID)."""
    response = requests.post(f"{IPFS_API_URL}/name/resolve", params={"arg": f"/ipns/{key_name}"})
    if response.status_code != 200:
        raise Exception(f"Failed to resolve IPNS: {response.text}")
    
    path = response.json()["Path"]
    cid = path.split("/")[-1]
    print(f"Resolved IPNS key '{key_name}' to CID: {cid}")
    return cid

def fetch_iparo_from_ipns(cid):
    """Fetch and deserialize an IPARO object from IPFS by CID."""
    response = requests.post(f"{IPFS_API_URL}/cat?arg={cid}")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch from IPFS: {response.status_code}")
    iparo = pickle.loads(response.content)
    return iparo

new_iparo = create_iparo()
key = generate_key_for_url(new_iparo.url)
ipns_id = get_ipns_name_for_key(key)
cid = add_iparo_to_ipfs(new_iparo)
ipns_name = update_ipns(cid, key)
resolved_cid = resolve_ipns_to_cid(ipns_id)
iparo_from_ipns = fetch_iparo_from_ipns(resolved_cid)
print(iparo_from_ipns)
print(iparo_from_ipns.__dict__)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
