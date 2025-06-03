import sys
import json
import pathlib
import requests
from flask import Flask, request, jsonify, make_response
from urllib.parse import urljoin
from datetime import datetime, timezone
from system.IPAROFactory import IPAROFactory
from system.IPFS import IPFS
from system.IPAROLinkFactory import IPAROLinkFactory
from system.IPNS import IPNS
from system.SnapshotsUtils import get_all_snapshots_for_url

app = Flask(__name__)

ipfs = IPFS()
ipns = IPNS()
iparo_link_factory = IPAROLinkFactory()

# Load or generate IPNS records cache
cache_path = pathlib.Path(__file__).parent.parent / 'ipns_records.json'
if cache_path.exists():
    with open(cache_path, 'r') as f:
        ipns_records = json.load(f)
    print(f"Loaded IPNS records from cache: {cache_path}")
else:
    ipns_records = IPAROFactory.create_and_store_iparos(ipfs, ipns, iparo_link_factory)
    with open(cache_path, 'w') as f:
        json.dump(ipns_records, f)
    print(f"Generated and saved IPNS records to cache: {cache_path}")

@app.route("/")
def index():
    return "Welcome to the IPARO Web Server"


@app.route("/archive", methods=["POST"]) # type: ignore
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


@app.route("/api/snapshot/<cid>", methods=["GET"])
def get_snapshot_metadata(cid):
    if not cid:
        return jsonify({"error": "Missing 'cid' path parameter"}), 400
    try:
        iparo = ipfs.retrieve(cid)
        return jsonify({
            "id": cid,
            "url": iparo.url,
            "timestamp": iparo.timestamp,
            "mementoUrl": f"/api/archive/{cid}/content"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/archive/<cid>/content", methods=["GET"])
def get_snapshot_content(cid):
    if not cid:
        return jsonify({"error": "Missing 'cid' path parameter"}), 400

    try:
        iparo = ipfs.retrieve(cid)
        # Strip HTTP headers from raw WARC response record
        raw = iparo.content
        sep = b"\r\n\r\n"
        body = raw.split(sep, 1)[1] if sep in raw else raw
        response = make_response(body)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/archive/<cid>/<path:subpath>", methods=["GET"])
def get_snapshot_resource(cid, subpath):
    if not cid or not subpath:
        return jsonify({"error": "Missing parameters"}), 400
    try:
        iparo = ipfs.retrieve(cid)
        # Construct full URL of resource
        original_base = iparo.url
        target_url = urljoin(original_base, subpath)
        # Fetch resource from live web
        resp = requests.get(target_url, timeout=10)
        if resp.status_code != 200:
            return jsonify({"error": f"Resource fetch failed with status {resp.status_code}"}), resp.status_code
        # Stream content back
        response = make_response(resp.content)
        response.headers['Content-Type'] = resp.headers.get('Content-Type', 'application/octet-stream')
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500






@app.route("/api/snapshots/date", methods=["GET"])
def get_snapshots_by_date():
    url      = request.args.get("url")
    date_str = request.args.get("date")
    limit    = request.args.get("limit", type=int, default=3)

    if not url or not date_str:
        return jsonify({"error": "Missing 'url' or 'date' parameter"}), 400

    try:
        all_snaps = get_all_snapshots_for_url(url, ipns, ipfs, ipns_records)
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        snaps = []
        for cid, iparo in all_snaps.items():
            date_part = iparo.timestamp.split("T", 1)[0]
            parts = date_part.split("-")

            if len(parts) == 3:
                snap_date = datetime.strptime(date_part, "%Y-%m-%d").date()
            elif len(parts) == 2:
                snap_date = datetime.strptime(f"{parts[0]}-{parts[1]}-01", "%Y-%m-%d").date()
            else:
                snap_date = datetime.strptime(f"{parts[0]}-01-01", "%Y-%m-%d").date()

            delta_days = abs((snap_date - target_date).days)
            snaps.append((delta_days, cid, iparo))

        snaps.sort(key=lambda x: x[0])
        selected = snaps[:limit]

        return jsonify([
            {"cid": cid, "url": iparo.url, "timestamp": iparo.timestamp}
            for _, cid, iparo in selected
        ]), 200

    except Exception as e:
        import traceback, sys
        traceback.print_exc(file=sys.stderr)
        return jsonify({"error": str(e)}), 500
    


if __name__ == "__main__":
    # Load or generate IPNS records cache
    cache_path = pathlib.Path(__file__).parent.parent / 'ipns_records.json'
    if cache_path.exists():
        with open(cache_path, 'r') as f:
            ipns_records = json.load(f)
        print(f"Loaded IPNS records from cache: {cache_path}")
    else:
        ipns_records = IPAROFactory.create_and_store_iparos(ipfs, ipns, iparo_link_factory)
        with open(cache_path, 'w') as f:
            json.dump(ipns_records, f)
        print(f"Generated and saved IPNS records to cache: {cache_path}")
    for url, peer_id in ipns_records.items():
        print(f"{url} -> {peer_id}")
    app.run(host='0.0.0.0', port=5002, debug=True, use_reloader=False)