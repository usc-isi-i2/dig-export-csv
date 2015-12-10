__author__ = 'amandeep'

from flask import Flask
import sys
from flask import request
import json
from elasticsearch_manager import ElasticSearchManager
from dig_bulk_folders import BulkFolders

application = Flask(__name__)


@application.route('/')
def hello():
    return 'hello'

@application.route('/export/csv',methods=['POST'])
def processcsv():
    try:
        json_data = json.loads(str(request.get_data()))
        esm=ElasticSearchManager()

        es_request = esm.convert_csv_to_esrequest(json_data['csv'])

        if 'size' in json_data:
            size=json_data['size']
        else:
            size='20'
        bf =BulkFolders()

        result = ''

        phone_field = 'hasFeatureCollection.phonenumber_feature.phonenumber'
        if 'ids' in es_request:
            result= result + process_results(bf,esm.search_es(esm.create_ids_query(es_request['ids']),None))
        if 'phone' in es_request:
            result = result + process_results(bf,esm.search_es(esm.create_terms_query(phone_field,es_request['phone']),int(size))) + '\n'

        return result
    except Exception as e:
        print >> sys.stderr,e
        loge(str(e))

@application.route('/export/<username>',methods=['POST'])
def get_user_folders(username):

    json_data=json.loads(str(request.get_data()))
    password=json_data['password']
    bf = BulkFolders()
    return bf.construct_tsv_response(bf.dereference_uris(bf.construct_uri_to_folder_map(bf.get_folders(username,password))))


@application.route('/export/postids',methods=['POST'])
def get_post_ids():
    try:
        json_data=json.loads(str(request.get_data()))

        if 'size' in json_data:
            size=json_data['size']
        else:
            size='20'

        postids=json_data['postids'].split(',')
        result=''
        esm = ElasticSearchManager()
        bf=BulkFolders()
        for postid in postids:
            res=esm.search_es(esm.create_postid_query(postid),int(size))
            hits=res['hits']['hits']
            ads=[]
            for hit in hits:
                ads.append(hit['_source'])
            for ad in ads:
                if postid in ad['url']:
                    tab_separated="\t".join(bf.ht_to_array(ad))
                    result = result + tab_separated + '\n'

        print result
        return result

    except Exception as e:
        print >> sys.stderr,e
        loge(str(e))

def process_results(bf,res):
    result=''
    hits = res['hits']['hits']
    ads=[]
    for hit in hits:
        ads.append(hit['_source'])

    for ad in ads:
        tab_separated = "\t".join(bf.ht_to_array(ad))
        result = result + tab_separated + '\n'
    return result[:result.rfind('\n')]


def loge(message):

    application.logger.error('Error:' + message)

def logi(message):

    application.logger.info('INFO:' + message)

if __name__ == "__main__":
    application.run()