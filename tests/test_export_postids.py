__author__ = 'amandeep'

import requests


url='http://localhost:5000/export/postids'
postid='20212377'
data={}
data['postids']=postid

r=requests.post(url,json = {"postids":postid})
print r._content

