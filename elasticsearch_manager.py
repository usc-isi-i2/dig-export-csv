__author__ = 'amandeep'

import json
import ConfigParser
from elasticsearch import Elasticsearch
from flask import Flask

app = Flask(__name__)

class ElasticSearchManager(object):

    def __init__(self):
        configuration = ConfigParser.RawConfigParser()
        configuration.read('config.properties')
        self.eshostname=configuration.get('ElasticSearch','host')
        self.esport=configuration.get('Elasticsearch','port')
        self.esprotocol=configuration.get('Elasticsearch','protocol')
        self.index=configuration.get('Elasticsearch','index')
        self.type=configuration.get('Elasticsearch','type')
        self.esusername=configuration.get('Elasticsearch','username')
        self.espassword=configuration.get('Elasticsearch','password')
        self.es = self.getESObject()

    def getESObject(self):

        if self.esusername.strip() != '' and self.espassword.strip() != '':
            esUrl = self.esprotocol+'://' + self.esusername + ":" + self.espassword + "@" + self.eshostname + ':' + str(self.esport)
        else:
            esUrl = self.esprotocol+'://' + self.eshostname + ':' + str(self.esport)

        es = Elasticsearch([esUrl], show_ssl_warnings=False)
        return es

    def search_es(self,query):
        res = self.es.search(index=self.index,doc_type=self.type, body=query)
        return res

    def convert_csv_to_esrequest(self,csv_text):
        lines=csv_text.split('\n')

        es_request={}
        ids = []
        phonenumbers = []

        #line is of format - uri,phonenumber etc
        for line in lines:
            data=line.split(',')
            if data[0].strip() != '':
                ids.append((data[0]))
            if data[1].strip() != '':
                phonenumbers.append((data[1]))

        es_request["ids"]=ids
        es_request["phone"]=phonenumbers

        return es_request

    def create_ids_query(self,ids):
        return json.dumps({'query':{'ids':{'values':ids}}})

    def create_terms_query(self,field, values):
        return json.dumps({'query':{'filtered':{'terms':{field:values}}}})
