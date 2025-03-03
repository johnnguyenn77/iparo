from dataclasses import dataclass
import IPAROLink


@dataclass
class IPARO:
    # Headers
    url: str
    timestamp: str
    seq_num: int
    linked_iparos: set[IPAROLink]
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