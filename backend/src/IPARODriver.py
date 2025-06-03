from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

# Import IPARO components
from IPFS import ipfs, Mode # type: ignore
from IPNS import ipns # type: ignore
from IPARO import IPARO
from IPAROFactory import IPAROFactory
from IPARODateConverter import IPARODateConverter # type: ignore

app = Flask(__name__)

# Configure CORS properly
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Add global CORS headers for all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

# Move get_all_cids to IPFS class
def get_all_cids(url):
    """
    Get all CIDs for a given URL by traversing from the latest node.
    """
    latest_cid = ipns.get_latest_cid(url)
    if not latest_cid:
        return []
        
    cids = set()
    
    def collect_cids(cid):
        if cid in cids:
            return
            
        cids.add(cid)
        node = ipfs.retrieve(cid)
        
        if node:
            for link in node.linked_iparos:
                collect_cids(link.cid)
    
    collect_cids(latest_cid)
    return list(cids)

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'  # For development
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

# Sample WARC URLs
SAMPLE_WARCS = [
    {"name": "Wikipedia COVID-19", "url": "https://en.wikipedia.org/wiki/COVID-19_pandemic"},
    {"name": "GitHub", "url": "https://github.com"}
]



@app.route('/api/samples', methods=['GET', 'OPTIONS'])
def get_samples():
    if request.method == 'OPTIONS':
        return add_cors_headers(jsonify({}))
    response = jsonify(SAMPLE_WARCS)
    return add_cors_headers(response)

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_url():
    if request.method == 'OPTIONS':
        return jsonify({})
    data = request.json
    url = data.get('url') # type: ignore
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    try:
        # Create a new IPARO node for the URL
        # In a real implementation, you would fetch the content from the URL
        content = f"Content from {url} at {datetime.now().isoformat()}".encode('utf-8')
        iparo = IPAROFactory.create_node(url, content) # type: ignore
        
        # Store in IPFS
        cid = ipfs.store(iparo)
        
        # Update IPNS
        ipns.update(url, cid)
        
        # Get the node we just stored
        stored_iparo = ipfs.retrieve(cid)
        
        # Return the node data
        return jsonify({
            "success": True,
            "data": iparo_to_dict(stored_iparo), # type: ignore
            "cid": cid
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/nodes', methods=['GET', 'OPTIONS'])
def get_nodes():
    if request.method == 'OPTIONS':
        return jsonify({})
    url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    try:
        # Get the latest CID for the URL
        latest_cid = ipns.get_latest_cid(url)
        if not latest_cid:
            return jsonify({"success": True, "nodes": []})
        
        # Get the node and its linked nodes
        nodes = []
        processed_cids = set()
        
        def process_node(cid):
            if cid in processed_cids:
                return
            
            processed_cids.add(cid)
            iparo = ipfs.retrieve(cid)
            
            if iparo:
                nodes.append({
                    "cid": cid,
                    "data": iparo_to_dict(iparo) # type: ignore
                })
                
                # Process linked nodes
                for link in iparo.linked_iparos:
                    process_node(link.cid)
        
        # Start with the latest node
        process_node(latest_cid)
        
        return jsonify({
            "success": True,
            "nodes": nodes
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/graph', methods=['GET', 'OPTIONS'])
def get_graph():
    if request.method == 'OPTIONS':
        return jsonify({})
    url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    try:
        cids = ipfs.get_all_cids(url)
        nodes = []
        links = []
        node_map = {}
        
        for i, cid in enumerate(cids):
            iparo = ipfs.retrieve(cid)
            if not iparo:
                continue
                
            node_data = iparo_to_dict(iparo) # type: ignore
            node_id = f"node_{i}"
            nodes.append({
                "id": node_id,
                "cid": cid,
                "label": f"Node {iparo.seq_num}",
                "timestamp": iparo.timestamp,
                "group": 1
            })
            node_map[cid] = node_id
        
        # Add links after all nodes are processed
        for cid in cids:
            iparo = ipfs.retrieve(cid)
            if not iparo:
                continue
                
            source_id = node_map[cid]
            for link in iparo.linked_iparos:
                if link.cid in node_map:
                    links.append({
                        "source": source_id,
                        "target": node_map[link.cid],
                        "value": 1
                    })
        
        return jsonify({
            "success": True,
            "nodes": nodes,
            "links": links
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)