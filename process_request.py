__author__ = 'amandeep'

from flask import Flask
import sys
from flask import request
import json
from elasticsearch_manager import ElasticSearchManager
from dig-bulk-folders import BulkFolders

app = Flask(__name__)

@app.route('/export/csv',methods=['POST'])
def processcsv():
    try:
        json_data = json.loads(str(request.get_data()))
        esm=ElasticSearchManager()

        bf = BulkFolders()

        es_request = esm.convert_csv_to_esrequest(json_data['csv'])

        if 'ids' in es_request:
            return process_results(esm.search_es(esm.create_ids_query(es_request['ids'])))
        if 'phone' in es_request:
            return process_results(esm.search_es(esm.create_terms_query('phone',es_request['phone'])))

    except Exception as e:
        print >> sys.stderr,e
        loge(str(e))

@app.route('/export/<username>',method=['GET'])
def get_user_folders(username):
    bf = BulkFolders()
    return bf.construct_tsv_response(bf.dereference_uris(bf.construct_uri_to_folder_map(bf.get_folders(username))))


@app.route('/export/postids',method=['POST'])
def get_post_ids():
    try:
        json_data=json.loads(str(request.get_data()))
        postids=json_data['postids'].split(',')
        result=[]
        esm = ElasticSearchManager()
        bf=BulkFolders()
        for postid in postids:
            res=esm.search_es(esm.create_postid_query(postid))
            hits=res['hits']['hits']
            ads=map(lambda x:x['_source'],hits)
            for ad in ads:
                if postid in ad['url']:
                    tab_separated="\t".join(bf.ht_to_array(ad))
                    result.append(tab_separated)

        return result

    except Exception as e:
        print >> sys.stderr,e
        loge(str(e))

def process_results(bf,res):
    result=[]

    hits = res['hits']['hits']
    ads = map(lambda x: x['_source'], hits)
    for ad in ads:
        tab_separated = "\t".join(bf.ht_to_array(ad))
        result.append(tab_separated)
    return result


def loge(message):

    app.logger.error('Error:' + message)

def logi(message):

    app.logger.info('INFO:' + message)