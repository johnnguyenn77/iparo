from datetime import datetime

from iparo.Exceptions import IPARONotFoundException
from iparo.IPARODateConverter import IPARODateConverter


class IPNS:

    def __init__(self):
        """
        Initialize the IPNS object with an empty hashmap for storing CIDs
        and counters for tracking operations.
        """
        self.__store: dict[str, str] = {}
        self.__versions: dict[tuple[str, str], str] = {}
        self.update_count = 0
        self.get_count = 0

    # Add parameter datetime - str
    def update(self, url: str, cid: str, timestamp: str = 'latest'):
        """
        Updates the latest CID for a given URL with a given timestamp.

        Args:
            url (str): The URL of the website.
            cid (str): The CID of the latest capture.
            timestamp (str): The string containing the timestamp (YYYY-mm-dd hh:mm:ss).
            Default is latest.
        """
        self.update_count += 1
        curr_timestamp = IPARODateConverter.datetime_to_str(datetime.now()) if timestamp == 'latest' else timestamp

        # /archive/latest/{url} -> value of URL, map it to the CID [default]
        self.__store[url] = cid

        # /archive/{datetime}/{url} -> convert datetime, map it to the CID
        self.__versions[(url, curr_timestamp)] = cid

    # Optional parameter: datetime ([un]serialized), default value is latest.
    def get_latest_cid(self, url: str) -> str:
        """
        Retrieves the latest CID for a given URL if it exists, else None.

        Args:
            url (str): The URL of the website.

        Returns:
            str: The CID of the latest capture for the given URL if it exists, else None.

        Exceptions:
            EmptyError: If the URL is not found.
        """
        self.get_count += 1
        if url not in self.__store:
            raise IPARONotFoundException(url)
        return self.__store[url]

    def get_cid(self, url: str, timestamp: str) -> str:
        """
        Retrieves the CID for a given timestamp.

        Args:
            url (str): The URL of the website.
            timestamp (str): The 14-character-long timestamp for the

        Returns:
            str: The CID of the latest capture for the given URL if it exists, else None.
        """
        self.get_count += 1
        return self.__versions[(url, timestamp)]

    def get_counts(self):
        """
        Returns the number of update and get operations performed.

        Returns:
            dict: Dictionary with the counts of update and get operations.
        """
        return {"get": self.get_count, "update": self.update_count}

    def reset_data(self):
        """
        Resets the data.
        """
        self.__store: dict[str, str] = {}

    def reset_counts(self):
        """
        Resets the operating counts. Used for the evaluation phase.
        """
        self.update_count = 0
        self.get_count = 0

    def get_store(self):
        return self.__store


ipns = IPNS()
