__author__ = 'amandeep'

from flask import Flask
import sys
from flask import request
import json
from elasticsearch_manager import ElasticSearchManager

app = Flask(__name__)

@app.route('/export/csv',methods=['POST'])
def processcsv():
    try:
        json_data = json.loads(str(request.get_data()))
        esm=ElasticSearchManager()

        es_request = esm.convert_csv_to_esrequest(json_data['csv'])

        if 'ids' in es_request:
            process_results(esm.search_es(esm.create_ids_query(es_request['ids'])))
        if 'phone' in es_request:
            process_results(esm.search_es(esm.create_terms_query('phone',es_request['phone'])))


    except Exception as e:
        print >> sys.stderr,e
        loge(str(e))



def process_results(res):
    return res

def loge(message):

    app.logger.error('Error:' + message)

def logi(message):

    app.logger.info('INFO:' + message)