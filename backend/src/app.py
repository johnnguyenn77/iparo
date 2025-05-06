from flask import Flask
from system.IPAROFactory import IPAROFactory
from system.IPFS import IPFS
from system.IPAROLinkFactory import IPAROLinkFactory
from system.IPNS import IPNS

app = Flask(__name__)
ipfs = IPFS()
ipns = IPNS()
iparo_link_factory = IPAROLinkFactory()

# track key and peer_id of websites
ipns_records = IPAROFactory.create_and_store_iparos(ipfs, ipns, iparo_link_factory)

for url, peer_id in enumerate(ipns_records.items()):
    print(url, peer_id)
    
@app.route("/") 
def get_iparos(): 
    return 
    
@app.route("/") 
def index(): 
    return 

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
