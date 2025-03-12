from datetime import datetime, timedelta

from iparo.IPARO import IPARO
from iparo.IPARODateConverter import IPARODateConverter

time1 = datetime.now().replace(microsecond=0)
time2 = time1 + timedelta(seconds=1)
URL = "https://www.example.com"
URL1 = "https://www.example1.com"
URL2 = "https://www.example2.com"
CID1 = "abcdefg"
CID2 = "bcdefgh"
iparo1 = IPARO(content=b"123456", timestamp=IPARODateConverter.datetime_to_str(time1), url="https://www.example.com",
               linked_iparos=set(), seq_num=0)
iparo2 = IPARO(content=b"1234567", timestamp=IPARODateConverter.datetime_to_str(time2), url="https://www.example.com",
               linked_iparos=set(), seq_num=1)
