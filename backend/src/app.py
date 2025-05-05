from flask import Flask
from system.IPAROFactory import IPAROFactory
from system.IPFS import IPFS

from system.IPNS import IPNS

app = Flask(__name__)
ipfs = IPFS()
ipns = IPNS()

# track key and peer_id of websites
ipns_records = IPAROFactory.create_and_store_iparos(ipfs, ipns)

for url, peer_id in enumerate(ipns_records.items()):
    print(url, peer_id)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
