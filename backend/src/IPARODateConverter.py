from datetime import datetime


class IPARODateConverter:
    """
    The date converter class converts a string to a datetime and a datetime to a string.
    """
    @classmethod
    def str_to_datetime(cls, timestamp: str):
        return datetime.strptime(timestamp, "%Y%m%d%H%M%S")

    @classmethod
    def datetime_to_str(cls, timestamp: datetime):
        return timestamp.strftime("%Y%m%d%H%M%S")

    @classmethod
    def diff(cls, timestamp1: str, timestamp2: str):
        """
        Calculates the difference between two timestamps. The result is
        equal to ``str_to_datetime(timestamp1) - str_to_datetime(timestamp2)``.
        :param timestamp1: The first timestamp
        :param timestamp2: The second timestamp
        :return:
        """
        return IPARODateConverter.str_to_datetime(timestamp1) - IPARODateConverter.str_to_datetime(timestamp2)