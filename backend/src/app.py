import requests
from flask import Flask, request, jsonify
from IPARO import IPARO
from io import BytesIO
from warcio.archiveiterator import ArchiveIterator
from warcio.recordloader import ArchiveLoadFailed
from collections import defaultdict

app = Flask(__name__)

IPFS_API_URL = "http://127.0.0.1:5001/api/v0"

def push_to_ipfs():
    """Processes WARC file, creates IPARO objects, and pushes them to IPFS and IPNS."""
    
    with open('../samples/warcs/mkelly2.warc', 'rb') as stream:
        for record in ArchiveIterator(stream):
            if record.rec_type == 'response':
                url = record.rec_headers.get_header('WARC-Target-URI')
                timestamp = record.rec_headers.get_header('WARC-Date')
                content = record.content_stream().read()

                # use IPNS to get the latest IPARO object
                # if it does not exist, create a new iparo object
                if fetch_ipns_data():
                # implement logic to get all the information from the IPNS and create a new IPARO object based on the information from the latest node
                # how do the ipns know which IPARO is belong to the current URL we used to archive 
                    pass
                else:
                    iparo_object = IPARO(
                        url=url,
                        timestamp=timestamp,
                        seq_num=0,
                        linked_iparos=set(),
                        content=content
                    )

                # Convert IPARO object to string (uses IPARO.__str__())
                iparo_string = str(iparo_object)

                # Push to IPFS
                ipfs_hash = add_to_ipfs(iparo_string)
                print(f"Stored IPARO for {url} at {ipfs_hash}")

                # Update IPNS with new hash
                ipns_name = update_ipns(ipfs_hash)
                print(f"Updated IPNS name: {ipns_name} → {ipfs_hash}")


def add_to_ipfs(data):
    """Uploads data to IPFS using HTTP API."""
    response = requests.post(f"{IPFS_API_URL}/add", files={"file": data.encode()})
    return response.json()["Hash"]  # Returns the IPFS CID


def update_ipns(ipfs_hash):
    """Pins an IPFS hash to IPNS using HTTP API."""
    response = requests.post(f"{IPFS_API_URL}/name/publish", params={"arg": f"/ipfs/{ipfs_hash}"})
    return response.json().get("Name", "Unknown IPNS Name")

def fetch_ipfs_data(ipfs_hash):
    """Fetches data from IPFS."""
    response = requests.get(f"https://ipfs.io/ipfs/{ipfs_hash}")
    return response.text

def fetch_ipns_data(ipns_name):
    """Fetches the latest IPFS hash from IPNS."""
    response = requests.get(f"https://ipfs.io/ipns/{ipns_name}")
    return response.text

# Example: Fetch data from IPFS
ipfs_hash = "QmbaEwpvQzv2YxHbhZuHx21mHi7f9Z41UjWZVbQ62Qcawe"
data = fetch_ipfs_data(ipfs_hash)
print("Fetched Data from IPFS:", data)

# Example: Fetch latest data from IPNS
ipns_name = "k51qzi5uqu5dkhyhede38jkwerpjr225c5wasm97ixvc3avgs1bbb6lao875k5"
latest_data = fetch_ipns_data(ipns_name)
print("Fetched Latest Data from IPNS:", latest_data)

# Run the function to push WARC data to IPFS/IPNS
push_to_ipfs()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
