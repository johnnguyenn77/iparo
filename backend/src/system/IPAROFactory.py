from warcio import ArchiveIterator
from warcio.exceptions import ArchiveLoadFailed  # new import
import os
from src.system.IPARO import IPARO


class IPAROFactory:
    @classmethod
    def create_and_store_iparos(cls, ipfs, ipns, iparo_link_factory, filename=None):
        """Processes one or more WARC files, creates and stores IPARO objects."""
        # Resolve samples/warcs folder relative to project root
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..')
        )
        warc_dir = os.path.join(project_root, 'samples', 'warcs')

        # build list of full paths to WARC files to process
        if filename is None:
            # all .warc files in the directory
            warc_paths = [
                os.path.join(warc_dir, fn)
                for fn in os.listdir(warc_dir)
                if fn.lower().endswith('.warc')
            ]
        elif isinstance(filename, (list, tuple)):
            warc_paths = [os.path.join(warc_dir, fn) for fn in filename]
        else:
            warc_paths = [os.path.join(warc_dir, filename)]

        key_name = {}

        # now process each WARC in turn
        for warc_path in warc_paths:
            print(f"== processing {os.path.basename(warc_path)} ==")
            with open(warc_path, 'rb') as stream:
                try:
                    for record in ArchiveIterator(stream):
                        if record.rec_type != 'response':
                            continue

                        url = record.rec_headers.get_header('WARC-Target-URI')
                        timestamp = record.rec_headers.get_header('WARC-Date')
                        content_type = record.rec_headers.get_header('Content-Type')
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
                                link = iparo_link_factory.from_cid_iparo(
                                    resolved_cid.split('/', 2)[-1], latest_node
                                )
                                linked_iparos.add(link)
                                print(f"Found previous IPARO for {url}")
                            else:
                                print("Resolved node mismatch; creating new head")
                        except Exception:
                            print("No previous IPARO; creating initial node")

                        # Create, store, and publish
                        iparo = IPARO(
                            url=url,
                            timestamp=timestamp,
                            seq_num=seq_num,
                            linked_iparos=frozenset(linked_iparos),  # type: ignore
                            content_type=content_type,
                            content=content,
                            nonce=0
                        )
                        cid = ipfs.store(iparo)
                        ipns.update(peer_id, cid)
                        print(f"Published version {seq_num} for {url} → {cid}\n")
                except ArchiveLoadFailed as e:
                    print(f"⚠️ Skipping broken WARC {os.path.basename(warc_path)}: {e}")
                    continue

                url = record.rec_headers.get_header('WARC-Target-URI')
                timestamp = record.rec_headers.get_header('WARC-Date')
                content_type = record.rec_headers.get_header('Content-Type')
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
                        link = iparo_link_factory.from_cid_iparo(resolved_cid.split('/', 2)[-1], latest_node)
                        linked_iparos.add(link)

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
                    content_type=content_type,
                    content=content,
                    nonce=0
                )
                cid = ipfs.store(iparo)

                # Publish new version to IPNS
                ipns.update(peer_id, cid)

                print(f"Published version {seq_num} for {url} with CID: {cid}\n")

        return key_name
