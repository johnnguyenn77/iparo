import hashlib

import requests

from system.Utils import Utils

class IPNS:

    def generate_key_for_url(self, url):
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        key_name = f"urlkey-{url_hash[:10]}"

        existing_keys = requests.post(f"{Utils.IPFS_API_URL}/key/list").json()
        if key_name not in [k["Name"] for k in existing_keys["Keys"]]:
            res = requests.post(f"{Utils.IPFS_API_URL}/key/gen", params={
                "arg": key_name,
                "type": "rsa",
                "size": "2048"
            })
            print(f"Generated new key: {key_name}")
        else:
            print(f"Using existing key: {key_name}")

        return key_name
    
    def get_name_for_key(self, key_name):
        response = requests.post(f"{Utils.IPFS_API_URL}/key/list").json()
        for key in response["Keys"]:
            if key["Name"] == key_name:
                return key["Id"]
        raise Exception(f"Key '{key_name}' not found")

    def update(self, key_name, cid):
        """Pins an IPFS hash to IPNS using a specific key."""
        response = requests.post(
            f"{Utils.IPFS_API_URL}/name/publish",
            params={
                "arg": f"/ipfs/{cid}",
                "key": key_name
            }
        )
        if response.status_code != 200:
            raise Exception(f"Failed to publish to IPNS: {response.text}")

        peer_id = response.json().get("Name", "Unknown IPNS Name")
        print(f"Published to IPNS: /ipns/{peer_id}")
        return peer_id

    def resolve_cid(self, peer_id):
        """Resolve IPNS key to the current IPFS hash (CID)."""
        response = requests.post(f"{Utils.IPFS_API_URL}/name/resolve", params={"arg": f"/ipns/{peer_id}"})
        if response.status_code != 200:
            raise Exception(f"Failed to resolve IPNS: {response.text}")

        path = response.json()["Path"]
        cid = path.split("/")[-1]
        print(f"Resolved IPNS key '{peer_id}' to CID: {cid}")
        return cid