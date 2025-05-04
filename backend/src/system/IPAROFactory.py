import os

from warcio import ArchiveIterator

from system.IPARO import IPARO


class IPAROFactory:
    @classmethod
    def create_iparo_from_warc(cls, filename=None):
        """Processes WARC file, creates IPARO object with incremented seq_num, pushes to IPFS."""
        # current_dir = os.path.dirname(os.path.abspath(__file__))
        warc_path = os.path.join('..', 'samples', 'warcs', '2mementos.warc')

        with open(warc_path, 'rb') as stream:
            for record in ArchiveIterator(stream):
                if record.rec_type == 'response':
                    url = record.rec_headers.get_header('WARC-Target-URI')
                    timestamp = record.rec_headers.get_header('WARC-Date')
                    content = record.content_stream().read()

                    iparo_object = IPARO(
                        url=url,
                        timestamp=timestamp,
                        seq_num=0,
                        linked_iparos=set(),
                        content=content,
                        nonce=0
                    )
                    return iparo_object