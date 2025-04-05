from datetime import datetime, timedelta

from iparo.IPARO import IPARO
from iparo.IPARODateFormat import IPARODateFormat

time1 = datetime.now().replace(microsecond=0)
time2 = time1 + timedelta(seconds=1)
URL = "https://www.example.com"
URL1 = "https://www.example1.com"
URL2 = "https://www.example2.com"
CID1 = "abcdefg"
CID2 = "bcdefgh"
iparo1 = IPARO(content=b"123456", timestamp=datetime.strftime(time1, IPARODateFormat.DATE_FORMAT), url="https://www.example.com",
               linked_iparos=set(), seq_num=0)
iparo2 = IPARO(content=b"1234567", timestamp=datetime.strftime(time2, IPARODateFormat.DATE_FORMAT), url="https://www.example.com",
               linked_iparos=set(), seq_num=1)
