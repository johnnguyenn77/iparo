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