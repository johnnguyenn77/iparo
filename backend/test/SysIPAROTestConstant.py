from system.IPARO import IPARO
from system.IPAROLink import IPAROLink


time1 = "2013-02-02T10:00:00Z"
url1 = "http://memento.us/"
content_type1 = "application/http; msgtype=response"
content1 = b"<html><body>Memento for 2/2/2013 10:00am</body></html>"
cid1 = 1
seq_num1 = 0

time2 = "2016-12-31T11:00:00Z"
url2 = "http://memento.us/"
content_type2 = "application/http; msgtype=response"
content2 = b"<html><body>Memento for 12/31/2016 11:00am</body></html>"
cid2 = 2
links2 = {IPAROLink(1, time1, cid1)}
seq_num2 = 1

time3 = "2017-12-31T11:00:00Z"
url3 = "http://someotherURI.us/"
content_type3 = "application/http; msgtype=response"
content3 = b"<html><body>SomeotherURI</body></html>"
cid3 = 3
seq_num3 = 0

time4 = "2018-12-31T11:00:00Z"
url4 = "http://anothersite.us/"
content_type4 = "application/http; msgtype=response"
content4 = b"<html><body>Another site</body></html>"
cid4 = 4
seq_num4 = 0

iparo1 = IPARO(
    url=url1,
    timestamp=time1,
    seq_num=seq_num1,
    linked_iparos=frozenset(),
    content_type=content_type1,
    content=content1,
    nonce=0
)

iparo2 = IPARO(
    url=url2,
    timestamp=time2,
    seq_num=seq_num2,
    linked_iparos=links2,
    content_type=content_type2,
    content=content2,
    nonce=0
)

iparo3 = IPARO(
    url=url3,
    timestamp=time3,
    seq_num=seq_num3,
    linked_iparos=frozenset(),
    content_type=content_type3,
    content=content3,
    nonce=0
)

iparo4 = IPARO(
    url=url4,
    timestamp=time4,
    seq_num=seq_num4,
    linked_iparos=frozenset(),
    content_type=content_type4,
    content=content4,
    nonce=0
)