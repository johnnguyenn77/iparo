from urllib.parse import urljoin, urlparse
import hashlib
import re
from flask import Flask, request, jsonify, make_response, abort
from warcio.archiveiterator import ArchiveIterator
from warcio.exceptions import ArchiveLoadFailed
import os, logging

# … your existing imports …

# suppress warcio noise
logging.getLogger('warcio').setLevel(logging.ERROR)

app = Flask(__name__)
_snapshots = []      # only HTML snapshots go here
_snapshot_data = {}  # all responses go here
_seen_html_keys = set()      # ← add this

def load_warcs():
    base = os.path.join(os.path.dirname(__file__), '..', 'samples', 'warcs')
    for fname in os.listdir(base):
        # include both uncompressed (.warc) and compressed (.warc.gz) archives
        if not (fname.endswith('.warc') or fname.endswith('.warc.gz')):
            continue
        path = os.path.join(base, fname)
        with open(path, 'rb') as stream:
            it = ArchiveIterator(stream)
            while True:
                try:
                    rec = next(it)
                except StopIteration:
                    break
                except ArchiveLoadFailed:
                    continue

                if rec.rec_type != 'response' or rec.http_headers is None:
                    continue

                url = rec.rec_headers.get_header('WARC-Target-URI')
                ts  = rec.rec_headers.get_header('WARC-Date')
                ct  = rec.http_headers.get_header('Content-Type') or 'application/octet-stream'
                body = rec.content_stream().read()
                key  = hashlib.sha256(f'{url}|{ts}'.encode()).hexdigest()

                # Store every response
                _snapshot_data[key] = {
                    'body': body,
                    'content_type': ct,
                    'url': url,
                    'timestamp': ts
                }

                # Only index each HTML memento once
                if ct.startswith('text/html') and key not in _seen_html_keys:
                    _seen_html_keys.add(key)
                    _snapshots.append({
                        'id': key,
                        'url': url,
                        'timestamp': ts,
                        'content_type': ct
                    })

# load all warcs on startup
load_warcs()

@app.route('/api/snapshots')
def list_snapshots():
    url = request.args.get('url')
    results = [s for s in _snapshots if s['url'] == url] if url else _snapshots
    return jsonify(results)

@app.route('/api/snapshots/date')
def snapshots_by_date():
    url   = request.args.get('url')
    date  = request.args.get('date')
    limit = int(request.args.get('limit', 3))
    matches = [s for s in _snapshots
               if s['url'] == url and s['timestamp'].startswith(date)]
    return jsonify(matches[:limit])

@app.route('/api/snapshot/<snap_id>')
def get_snapshot(snap_id):
    snap = next((s for s in _snapshots if s['id'] == snap_id), None)
    if not snap:
        abort(404)
    return jsonify({
        'id': snap['id'],
        'url': snap['url'],
        'timestamp': snap['timestamp'],
        'title': snap['url'],
        'mementoUrl': f'/api/archive/{snap_id}/content'
    })

@app.route('/api/archive/<snap_id>/', defaults={'path':'content'})
@app.route('/api/archive/<snap_id>/<path:path>')
def archive_resource(snap_id, path):
    # find the HTML snapshot metadata
    snap = next((s for s in _snapshots if s['id'] == snap_id), None)
    if not snap:
        abort(404)

    ts = snap['timestamp']
    # main HTML content
    if path == 'content':
        rec = _snapshot_data.get(snap_id)
    else:
        # compute directory base for correct URL resolution
        parsed = urlparse(snap['url'])
        if parsed.path.endswith('/'):
            base_dir = snap['url']
        else:
            head, _, _ = parsed.path.rpartition('/')
            base_dir = f"{parsed.scheme}://{parsed.netloc}{head}/"
        resource_url = urljoin(base_dir, path)
        # try exact match by timestamp
        key = hashlib.sha256(f'{resource_url}|{ts}'.encode()).hexdigest()
        rec = _snapshot_data.get(key)
        # fallback to any record with matching URL
        if rec is None:
            rec = next((r for r in _snapshot_data.values() if r['url'] == resource_url), None)

    if not rec:
        abort(404)

    body = rec['body']
    ct   = rec['content_type']

    if ct.startswith('text/html'):
        html = body.decode('utf-8', errors='ignore')
        # ensure standards mode
        if not html.lstrip().lower().startswith('<!doctype'):
            html = '<!DOCTYPE html>\n' + html
        # inject <base> into existing <head>
        def add_base(m):
            return m.group(1) + f"\n  <base href=\"/api/archive/{snap_id}/\" />"
        html, count = re.subn(r'(<head[^>]*>)', add_base, html, count=1, flags=re.IGNORECASE)
        if count == 0:
            # fallback wrap if no <head> found
            html = (
                '<!DOCTYPE html>\n'
                '<html lang="en">\n'
                '<head>\n'
                '  <meta charset="utf-8"/>\n'
                f'  <base href="/api/archive/{snap_id}/" />\n'
                '</head>\n'
                f'{html}\n'
                '</html>'
            )
        resp = make_response(html)
        resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    else:
        resp = make_response(body)
        resp.headers['Content-Type'] = ct

    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)