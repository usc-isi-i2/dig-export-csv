__author__ = 'amandeep'

import requests
import codecs

f=codecs.open('test_input.csv','r','utf-8')
lines=f.readlines()
f.close()

url='http://localhost:5000/api/ads/bulk-query'

r=requests.post(url,json={"csv":lines,"size":"40"})
print r._content


