__author__ = 'amandeep'

import requests


url='http://localhost:5000/export/postids'
#postids can be comma separated
postid='20212377'

r=requests.post(url,json = {"postids":postid,"size":"20"})
print r._content

