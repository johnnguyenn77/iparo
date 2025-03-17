from datetime import datetime
from typing import Optional

from iparo.Exceptions import IPARONotFoundException
from iparo.IPARO import IPARO
from iparo.IPARODateConverter import IPARODateConverter
from iparo.IPAROLink import IPAROLink
from iparo.IPFS import ipfs


class IPAROLinkFactory:
    """
    A collection of helper methods dealing with creating IPAROLinks
    """
    @classmethod
    def from_cid(cls, cid: str) -> Optional[IPAROLink]:
        """
        A helper method that takes in a CID and outputs an IPAROLink (or None if there is no such IPARO)
        :param cid: The CID of the IPARO.
        :return: The link to the IPARO if the CID is present.
        """
        iparo = ipfs.retrieve(cid)
        if iparo is None:
            return None
        return IPAROLink(seq_num=iparo.seq_num, timestamp=iparo.timestamp, cid=cid)

    @classmethod
    def from_cid_iparo(cls, cid: str, iparo: IPARO) -> IPAROLink:
        """
        A helper method that takes in a CID and the corresponding IPARO object, and
        outputs an IPAROLink. The assumption underlying the operation is that the
        IPARO's CID maps directly to the IPARO object. This will save an IPFS
        operation each time the method is called, and it does not require a check
        for ``None``.

        :param iparo: The IPARO object itself.
        :param cid: The CID of the IPARO.
        :return: The link to the IPARO
        """
        return IPAROLink(seq_num=iparo.seq_num, timestamp=iparo.timestamp, cid=cid)

    @classmethod
    def retrieve_nth_iparo(cls, link: IPAROLink, number: int) -> IPAROLink:
        """
        A helper method that enables the retrieval of IPARO using a sequence number
        to save IPARO operations by adding the ability to repeatedly apply the
        greedy search method.
        """
        if link.seq_num < number:
            raise IPARONotFoundException(number)
        elif link.seq_num == number:
            return link

        # It is assumed that there is a link to the previous node.
        iparo = ipfs.retrieve(link.cid)
        candidate_links = [link for link in iparo.linked_iparos if link.seq_num >= number]
        if not candidate_links:
            raise IPARONotFoundException(number)
        next_link = min(candidate_links, key=lambda link: link.seq_num)

        return IPAROLinkFactory.retrieve_nth_iparo(next_link, number)

    @classmethod
    def retrieve_closest_iparo(cls, link: IPAROLink, timestamp: datetime) -> IPAROLink:
        """
        A helper method that enables the retrieval of IPARO using a sequence number
        to save IPARO operations by adding the ability to repeatedly apply the
        greedy search method from an IPARO link. Unlike the other method, it only applies
        the closest IPARO.
        """
        curr_ts = IPARODateConverter.str_to_datetime(link.timestamp)

        # if ts > timestamp:
        #     raise IPARONotFoundException(ts)
        try:
            if curr_ts == timestamp:
                return link
            prev_link = IPAROLinkFactory.retrieve_nth_iparo(link, link.seq_num - 1)
            prev_ts = IPARODateConverter.str_to_datetime(prev_link.timestamp)
            # Calculate time fraction and see if it's greater than 0.5.
            time_frac = (timestamp - prev_ts) / (curr_ts - prev_ts)
            if 0 <= time_frac < 0.5:
                return prev_link
            elif 0.5 <= time_frac <= 1:
                return link
            elif 1 <= time_frac:
                raise IPARONotFoundException("Not a valid timestamp")
            else:
                iparo = ipfs.retrieve(prev_link.cid)
                candidate_links = iparo.linked_iparos
                candidate_links.add(prev_link)
                # Find minimum time
                next_link = min([link for link in candidate_links if
                                 IPARODateConverter.str_to_datetime(link.timestamp) >= timestamp],
                                key=lambda link: IPARODateConverter.str_to_datetime(link.timestamp))
                return IPAROLinkFactory.retrieve_closest_iparo(next_link, timestamp)
        except IPARONotFoundException as e:
            raise e
        except ValueError:
            raise IPARONotFoundException("No previous link")

    # @classmethod
    # def find_link(cls, iparo: IPARO, ):
    #     """
    #     Given an IPARO object, find a link with the given sequence number.
    #     """
    #     try:
    #         previous_link = [link for link in iparo.linked_iparos if link.seq_num == ]
    #         return previous_link[0]
    #     except IndexError:
    #         raise IPARONotFoundException(f"No link available for sequence number {seq_num}")

    @classmethod
    def from_indices(cls, link: IPAROLink, indices: set[int]) -> set[IPAROLink]:
        """
        A helper method that allows the IPFS to retrieve the selected versions of a URL,
        using the latest node.
        """
        sorted_indices = sorted(indices, reverse=True)
        curr_link = link
        links = set()
        for index in sorted_indices:
            curr_link = IPAROLinkFactory.retrieve_nth_iparo(curr_link, index)
            links.add(curr_link)

        return links

    @classmethod
    def from_timestamps(cls, link: IPAROLink, timestamps: set[datetime]):
        """
        Constructs a list of IPARO links from a set of timestamps.
        """
        sorted_timestamps = sorted(timestamps, reverse=True)
        links = set()
        for ts in sorted_timestamps:
            link = IPAROLinkFactory.retrieve_closest_iparo(link, ts)
            links.add(link)

        return links



