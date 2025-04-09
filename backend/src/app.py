import requests
from flask import Flask, request, jsonify
from iparo.IPARO import IPARO
from io import BytesIO
from warcio.archiveiterator import ArchiveIterator
from warcio.recordloader import ArchiveLoadFailed
import os

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
                
                print(url, timestamp)

            if get_latest_node():
            # implement logic to get all the information from the IPNS and create a new IPARO object based on the information from the latest node
            # how do the ipns know which IPARO is belong to the current URL we used to archive 
                pass
            else:
                iparo_object = IPARO(
                    url=url,
                    timestamp=timestamp,
                    seq_num=0,
                    linked_iparos=set(),
                    content=content,
                    nonce=0
                )


def get_latest_node(ipns_name=None):
    """Fetches the latest IPARO object from IPNS."""
    response = requests.get(f"https://ipfs.io/ipns/{ipns_name}")
    return response.text

create_iparo()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
