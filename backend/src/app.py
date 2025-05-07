from flask import Flask, request, jsonify, send_file
import datetime
import io
import mimetypes
import os
from system.IPAROFactory import IPAROFactory
from system.IPFS import IPFS
from system.IPAROLinkFactory import IPAROLinkFactory
from system.IPNS import IPNS
from system.IPARO import IPARO
from system.SnapshotsUtils import get_all_snapshots_for_url


app = Flask(__name__)

ipfs = IPFS()
ipns = IPNS()
iparo_link_factory = IPAROLinkFactory()

@app.route("/")
def index():
    return "Welcome to the IPARO Web Server"


@app.route("/archive", methods=["POST"])
def archive():
    pass


@app.route("/api/recent_snapshot", methods=["GET"])
def get_latest_snapshot():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing 'url'"}), 400
    
    peer_id = ipns_records.get(url)
    
    if not peer_id:
        return jsonify({"error": "This website never archived"}), 404
    
    cid = ipns.resolve_cid(peer_id)
    iparo = ipfs.retrieve(cid)
    
    return jsonify({
        "cid": cid,
        "timestamp": iparo.timestamp,
        "url": iparo.url,
        "content": iparo.content.decode("utf-8")
    })


@app.route("/api/snapshots", methods=["GET"])
def get_all_snapshots():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing 'url'"}), 400

    try:
        snapshots = get_all_snapshots_for_url(url, ipns, ipfs, ipns_records)
        return jsonify([
            {
                "timestamp": iparo.timestamp,
                "url": iparo.url,
                "seq_num": iparo.seq_num
            } for iparo in snapshots
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/snapshot/<cid>", methods=["GET"])
def get_snapshot_metadata(cid):
    pass


@app.route("/api/archive/<cid>/content", methods=["GET"])
def get_snapshot_content(cid):
    pass


@app.route("/api/archive/<cid>/<path:subpath>", methods=["GET"])
def get_snapshot_resource(cid, subpath):
    pass

if __name__ == "__main__":
    ipns_records = IPAROFactory.create_and_store_iparos(ipfs, ipns, iparo_link_factory)
    for url, peer_id in ipns_records.items():
        print(f"{url} -> {peer_id}")
    app.run(debug=True, use_reloader=False)
