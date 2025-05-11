import time

from simulation.IPARO import IPARO

time1 = int(1000000 * time.time())
time2 = int(1000000 * (time.time() + 1))
URL = "https://www.example.com"
URL1 = "https://www.example1.com"
URL2 = "https://www.example2.com"
CID1 = "abcdefg"
CID2 = "bcdefgh"
iparo1 = IPARO(content=b"123456", timestamp=time1, url="https://www.example.com",
               linked_iparos=set(), seq_num=0)
iparo2 = IPARO(content=b"1234567", timestamp=time2, url="https://www.example.com",
               linked_iparos=set(), seq_num=1)
