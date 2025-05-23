from dataclasses import dataclass
from system.IPAROLink import IPAROLink


@dataclass(frozen=True)
class IPARO:
    # Headers
    url: str
    timestamp: str
    seq_num: int
    linked_iparos: set[IPAROLink]
    content_type: str # frontend request
    # Body
    content: bytes
    # Trailer
    nonce: int = 0  # For now

    def __str__(self):
        """
        Returns a string representation of the IPARO object.

        Returns:
            str: A string containing the URL and content of the IPARO.
        """
        iparo = {
            "URL": self.url,
            "Content": self.content,
            "Timestamp": self.timestamp
        }
        return str(iparo)