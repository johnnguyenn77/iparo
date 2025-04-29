from flask import Flask
from system.IPAROFactory import IPAROFactory
from system.IPFS import IPFS

from system.IPNS import IPNS

app = Flask(__name__)
ipfs = IPFS()
ipns = IPNS()



new_iparo = IPAROFactory.create_iparo_from_warc()
cid = ipfs.store(new_iparo)
print(cid)
url_key = get
ipns_name = ipns.update(url_key, cid)
resolved_cid = ipns.resolve_cid(ipns_name)
print(resolved_cid)
iparo_from_ipns = ipfs.retrieve(resolved_cid)
print(iparo_from_ipns)
print(iparo_from_ipns.__dict__)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
