from datetime import datetime


class IPARODateConverter:
    """
    The date converter class converts a string to a datetime and a datetime to a string.
    The format is YYYYMMDDhhmmss.
    """
    @classmethod
    def str_to_datetime(cls, timestamp: str):
        """
        Converts a string into a datetime. This will return the corresponding ``datetime`` object.
        """
        return datetime.strptime(timestamp, "%Y%m%d%H%M%S")

    @classmethod
    def datetime_to_str(cls, timestamp: datetime):
        """
        Converts a datetime into a string. This will return the time string (to the nearest second).
        """
        return timestamp.strftime("%Y%m%d%H%M%S")

    @classmethod
    def diff(cls, timestamp1: str, timestamp2: str):
        """
        Calculates the difference between two timestamps. The result is
        equal to ``str_to_datetime(timestamp1) - str_to_datetime(timestamp2)``.

        Args:
            timestamp1 (str): The first timestamp string.
            timestamp2 (str): The second timestamp string.

        Returns:
            The difference between ``timestamp1`` and ``timestamp2``
        """
        return IPARODateConverter.str_to_datetime(timestamp1) - IPARODateConverter.str_to_datetime(timestamp2)