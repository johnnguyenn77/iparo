from datetime import datetime, timedelta


class IPARODateFormat:
    """
    The date formatter class converts a string to a datetime and a datetime to a string.
    The format is YYYY-MM-DDThh:mm:ss.ffffffZ, where the ffffff represents the 6 digits
    for the microseconds.
    """
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    """
    The date format string used to perform a conversion, based on the latest WARC version.
    """

    @classmethod
    def diff(cls, timestamp1: str, timestamp2: str):
        """
        Calculates the difference between two timestamps. The result is
        equal to `datetime.strptime(timestamp1, IPARODateFormat.DATE_FORMAT) -
        datetime.strptime(timestamp2, IPARODateFormat.DATE_FORMAT)`.

        Args:
            timestamp1 (str): The first timestamp string.
            timestamp2 (str): The second timestamp string.

        Returns:
            The difference between ``timestamp1`` and ``timestamp2``
        """
        ts1 = datetime.strptime(timestamp1, IPARODateFormat.DATE_FORMAT)
        ts2 = datetime.strptime(timestamp2, IPARODateFormat.DATE_FORMAT)

        return ts1 - ts2

    # Question: Should we have add_timedelta, add_timedeltas, or diff methods?
    @classmethod
    def add_timedelta(cls, timestamp: str, delta: timedelta):
        """
        Calculates the sum of a timestamp (given in string form) and a given time
        difference. The result is equal to
        ``datetime.strftime(datetime.strptime(timestamp, IPARODateFormat.DATE_FORMAT) + delta)``.

        Args:
            timestamp (str): The first timestamp string.
            delta (timedelta): The time difference.

        Returns:
            The sum of timestamp and delta.
        """
        return datetime.strftime(datetime.strptime(timestamp, IPARODateFormat.DATE_FORMAT) + delta,
                                 IPARODateFormat.DATE_FORMAT)

    @classmethod
    def add_timedeltas(cls, timestamp: str, deltas: list[timedelta]):
        """
        Calculates the sum of a timestamp (given in string form) and a given time
        difference. The result is equal to
        ``datetime.strftime(datetime.strptime(timestamp, IPARODateFormat.DATE_FORMAT) + delta)``
        The difference is that it will save many calls to `datetime.strptime`.

        Args:
            timestamp (str): The first timestamp string.
            deltas (list[timedelta]): The time differences.

        Returns:
            The list of sums of `timestamp` and `deltas`
        """
        ts = datetime.strptime(timestamp, IPARODateFormat.DATE_FORMAT)
        return [datetime.strftime(ts + delta, IPARODateFormat.DATE_FORMAT) for delta in deltas]
