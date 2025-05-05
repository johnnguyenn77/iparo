from warcio import ArchiveIterator
import os
import time
from system.IPARO import IPARO
from system.IPAROLink import IPAROLink

class IPAROFactory:
    @classmethod
    def create_and_store_iparos(cls, ipfs, ipns, filename=None):
        """Processes WARC file, creates and stores IPARO objects with proper version chaining."""
        warc_path = os.path.join('..', 'samples', 'warcs', '2mementos.warc')

        key_name = {}

        with open(warc_path, 'rb') as stream:
            for record in ArchiveIterator(stream):
                if record.rec_type != 'response':
                    continue

                url = record.rec_headers.get_header('WARC-Target-URI')
                timestamp = record.rec_headers.get_header('WARC-Date')
                content = record.content_stream().read()

                key_url = ipns.generate_key_for_url(url)
                peer_id = ipns.get_name_for_key(key_url)
                key_name[url] = peer_id

                seq_num = 0
                linked_iparos = set()

                try:
                    resolved_cid = ipns.resolve_cid(peer_id)
                    latest_node = ipfs.retrieve(resolved_cid.split('/', 2)[-1])

                    if latest_node and latest_node.url == url:
                        seq_num = latest_node.seq_num + 1
                        linked_iparos.add(IPAROLink(
                                seq_num=latest_node.seq_num,
                                timestamp=latest_node.timestamp,
                                cid=resolved_cid.split('/', 2)[-1]
                            ))

                        print(f"Found previous IPARO for {url}, current linked_iparoes: {linked_iparos}")
                    else:
                        print(f"Resolved node does not match expected URL or failed to load")
                except Exception as e:
                    print(f"No previous IPARO found for {url}, creating initial node")

                # Create and store IPARO
                iparo = IPARO(
                    url=url,
                    timestamp=timestamp,
                    seq_num=seq_num,
                    linked_iparos=frozenset(linked_iparos),
                    content=content,
                    nonce=0
                )
                cid = ipfs.store(iparo)

                # Publish new version to IPNS
                ipns.update(peer_id, cid)

                print(f"Published version {seq_num} for {url} with CID: {cid}\n")

        return key_name
