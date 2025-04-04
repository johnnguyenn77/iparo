from dataclasses import dataclass
from iparo.IPAROLink import IPAROLink


@dataclass
class IPARO:
    # Headers
    url: str
    timestamp: str
    seq_num: int
    linked_iparos: set[IPAROLink] # prior_iparos
    # Advantages: Time efficiency, disadvantages: space?
    # previous_link: IPAROLink
    # first_link: IPAROLink
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