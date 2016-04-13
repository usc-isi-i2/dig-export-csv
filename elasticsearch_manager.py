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
        self.eshostname = configuration.get('ElasticSearch', 'host')
        self.esport = configuration.get('ElasticSearch', 'port')
        self.esprotocol = configuration.get('ElasticSearch', 'protocol')
        self.index = configuration.get('ElasticSearch', 'index')
        self.type = configuration.get('ElasticSearch', 'type')
        self.esusername = configuration.get('ElasticSearch', 'username')
        self.espassword = configuration.get('ElasticSearch', 'password')
        self.es = self.get_es_object()
        self.num_of_retries = 3

    def get_es_object(self):

        if self.esusername.strip() != '' and self.espassword.strip() != '':
            esurl = self.esprotocol+'://' + self.esusername + ":" + \
                self.espassword + "@" + self.eshostname + ':' + str(self.esport)
        else:
            esurl = self.esprotocol+'://' + self.eshostname + ':' + str(self.esport)

        es = Elasticsearch([esurl], show_ssl_warnings=False)
        return es

    def search_es(self, query, size):
        if size is not None:
            query['size'] = size

        for i in range(0, self.num_of_retries):
            print 'Trial:', i
            res = self.es.search(index=self.index, doc_type=self.type, body=json.dumps(query))
            print res
            if res['timed_out'] is False:
                return res
            else:
                print "Request timed out, trying again"
                continue

        # try one last time
        res = self.es.search(index=self.index, doc_type=self.type, body=json.dumps(query))

        return res

    @staticmethod
    def create_ids_query(ids):
        return {'query': {'ids': {'values': ids}}}

    @staticmethod
    def create_terms_query(field, values):
        return {'query': {'filtered': {'filter': {'term': {field: values}}}}}

    @staticmethod
    def create_postid_query(post_id):
        return {'query': {'query_string': {'default_field': '_all', 'query': post_id}}}
