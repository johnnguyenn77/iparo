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
from system.SnapshotsUtils import get_all_snapshots_for_url, retrieve_closest_iparos

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
        return jsonify({"error": "This website has never been archived"}), 404
    
    cid = ipns.resolve_cid(peer_id)
    iparo = ipfs.retrieve(cid)
    
    return jsonify({
        "cid": cid,
        "url": iparo.url,
        "timestamp": iparo.timestamp,
        "seq_num": iparo.seq_num,
        "content_type": iparo.content_type
    }), 200


@app.route("/api/snapshots", methods=["GET"])
def get_all_snapshots():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing 'url'"}), 400

    try:
        snapshots = get_all_snapshots_for_url(url, ipns, ipfs, ipns_records)
        return jsonify([
            {
                "cid": cid,
                "url": iparo.url,
                "timestamp": iparo.timestamp,
                "seq_num": iparo.seq_num,
                "content_type": iparo.content_type
            } for cid, iparo in snapshots.items()
        ]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/snapshots/count", methods=["GET"])
def get_url_version_count():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing 'url' query parameter"}), 400
    
    peer_id = ipns_records.get(url)
    
    if not peer_id:
        return jsonify({"error": "This website has never been archived"}), 404
    
    cid = ipns.resolve_cid(peer_id)
    iparo = ipfs.retrieve(cid)
    version_count = iparo.seq_num + 1
    
    return jsonify({
        "url": iparo.url,
        "total_count": version_count
    }), 200


@app.route("/api/archive/<cid>/content", methods=["GET"])
def get_snapshot_content(cid):
    if not cid:
        return jsonify({"error": "Missing 'cid' path parameter"}), 400

    try:
        iparo = ipfs.retrieve(cid)
        print(iparo.content)
        return jsonify({
            "url": iparo.url,
            "content": iparo.content.decode('utf-8')
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/archive/<cid>/<path:subpath>", methods=["GET"])
def get_snapshot_resource(cid, subpath):
    pass


@app.route("/api/snapshots/date", methods=["GET"])
def get_url_versions_by_date():
    url: str = request.args.get("url")
    date: str = request.args.get("date")

    try:
        limit: int = request.args.get("limit", 3, type=int)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if not url or not date:
        return jsonify({"error": "Missing 'url' or 'date'"}), 400

    try:
        snapshots = retrieve_closest_iparos(url, ipns, ipfs, date, ipns_records, limit)
        return jsonify([{
                "cid": cid,
                "url": iparo.url,
                "timestamp": iparo.timestamp,
                "seq_num": iparo.seq_num,
                "content_type": iparo.content_type
            } for cid, iparo in snapshots.items()]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    ipns_records = IPAROFactory.create_and_store_iparos(ipfs, ipns, iparo_link_factory)
    for url, peer_id in ipns_records.items():
        print(f"{url} -> {peer_id}")

    app.run(debug=True, use_reloader=False)
