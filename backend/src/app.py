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


def get_latest_node(ipns_name=None):
    """Fetches the latest IPARO object from IPNS."""
    response = requests.get(f"https://ipfs.io/ipns/{ipns_name}")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch from IPNS: {response.status_code}")
    try:
        iparo_obj = pickle.loads(response.content)
        return iparo_obj
    except Exception as e:
        raise Exception(f"Failed to deserialize IPARO object: {e}")

def add_iparo_to_ipfs(iparo_obj):
    pickled_data = pickle.dumps(iparo_obj)
    response = requests.post(
        f"{IPFS_API_URL}/add",
        files={"file": ("iparo.pkl", pickled_data)}
    )
    print("Succesfully add to ipfs")
    print(f"IPFS Hash: {response.json()['Hash']}")
    return response.json()["Hash"]


def update_ipns(ipfs_hash):
    """Pins an IPFS hash to IPNS using HTTP API."""
    response = requests.post(f"{IPFS_API_URL}/name/publish", params={"arg": f"/ipfs/{ipfs_hash}"})
    return response.json().get("Name", "Unknown IPNS Name")

new_iparo = create_iparo()
key = generate_key_for_url(new_iparo.url)
cid = add_iparo_to_ipfs(new_iparo)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
