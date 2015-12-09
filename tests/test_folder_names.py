__author__ = 'amandeep'

import requests


username='memex'
url='http://localhost:5000/export/' + username

r=requests.post(url,json={"password":""})
print r._content


