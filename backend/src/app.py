from flask import Flask, request, jsonify
import requests
from warcio.warcwriter import WARCWriter
from warcio.recordloader import ArcWarcRecord
from io import BytesIO
import datetime
import os
from IPARO import IPARO
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

IPFS_API_URL = "http://127.0.0.1:5001/api/v0"
TARGET_DIR = "../data/"

os.makedirs(TARGET_DIR, exist_ok=True)

def inspect_response_and_create_iparo_object(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # Fetch the webpage
    response = requests.get(url, headers=headers)
    
    # Print Response Headers
    logging.debug("\nHeaders:")
    for key, value in response.headers.items():
        logging.debug(f"{key}: {value}")
        
    logging.debug("\Content:")
    logging.debug(response.content.body)
            
       # Print Cookies (if any)
    logging.debug("\nCookies:")
    for key, value in response.cookies.items():
        logging.debug(f"{key}: {value}")
            
    iparo_object = IPARO(
        url = url,
        timestamp= response.headers.get("Date"),
        seq_num=0,
        linked_iparos=(),
        content= response.content
    )
    
    return str(iparo_object)

def archive(iparo):
    
    # Generate a timestamped filename and path for archive file
    warc_filename = f"web_archive_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.warc.gz"
    warc_path = os.path.join(TARGET_DIR, warc_filename)


    # Create a WARC file and write the response
    with open(warc_path, "wb") as warc_file:
        warc_writer = WARCWriter(warc_file, gzip=True)

        # Create a valid WARC record
        
    return warc_path

# Example Usage
#warc_filename = f"web_archive_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.warc.gz"

@app.route("/get/<cid>", methods=["GET"])
def get_file(cid):
    return jsonify({"url": f"https://ipfs.io/ipfs/{cid}"})

@app.route('/archive_url', methods=['POST'])
def archive_url():
    """
    Fetch a web page, archive it in WARC format, store in IPFS, and return the CID.
    """
    data = request.json
    if 'url' not in data:
        return jsonify({"error": "No URL provided"}), 400
    
    url = data['url']
    iparo_object = inspect_response_and_create_iparo_object(url)
    
    return jsonify({"message": "URL processed", "iparo_object": iparo_object}), 200


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
