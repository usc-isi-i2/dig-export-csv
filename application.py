__author__ = 'amandeep'

import json
from flask import request
from flask import Response
from flask import make_response
from functools import wraps
from flask import Flask
from elasticsearch_manager import ElasticSearchManager
from dig_bulk_folders import BulkFolders
import ConfigParser

application = Flask(__name__)


phone_field = 'hasFeatureCollection.phonenumber_feature.phonenumber'
basic_username = None
basic_password = None


def init():
    global basic_username
    global basic_password

    if basic_username is None and basic_password is None:
        configuration = ConfigParser.RawConfigParser()
        configuration.read('config.properties')
        basic_username = configuration.get('BasicAuth', 'username')
        basic_password = configuration.get('BasicAuth', 'password')


def check_auth(username, password):
    return username is not None and password is not None


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


def requires_basic_auth(f):
    @wraps(f)
    def decorated_basic(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_basic_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated_basic


def check_basic_auth(username, password):
    init()
    return username == basic_username and password == basic_password


@application.route('/', methods=['GET'])
def instructions():
    return 'Read api details at - https://github.com/usc-isi-i2/dig-export-csv'


@application.route('/api/ads', methods=['GET'])
@requires_basic_auth
def get_ads():
    es = ElasticSearchManager()
    bf = BulkFolders()

    ad_id = request.args.get('uri')
    postids = request.args.get('post_ids')
    phone = request.args.get('phone')
    size = request.args.get('size')
    headings = request.args.get('heading')
    store = request.args.get('store')

    """first line columns names if headings = 1"""
    if headings is None:
        headings = '0'

    if size is None:
        size = "20"

    if headings == "1":
        result = "\t".join(bf.ht_headings) + '\n'
    else:
        result = ''

    if store is None:
        store = "1"

    try:
        if ad_id is not None:
            ids = [ad_id]
            result += process_results(bf, es.search_es(ElasticSearchManager.create_ids_query(ids), None))

            if store == "1":
                response = make_response(result)
                response.headers["Content-Disposition"] = "attachment; filename=data.tsv"
                return response
            else:
                return Response(result, 200)
    except Exception as e:
        return Response(str(e), 500)

    try:
        if postids is not None:
            post_ids = postids.split(',')
            for post_id in post_ids:
                res = es.search_es(ElasticSearchManager.create_postid_query(post_id), int(size))
                hits = res['hits']['hits']
                for hit in hits:
                    ad = hit['_source']
                    if post_id in ad['url']:
                        tab_separated = "\t".join(bf.ht_to_array(ad))
                        result = result + tab_separated + '\n'

            if store == "1":
                response = make_response(result)
                response.headers["Content-Disposition"] = "attachment; filename=data.tsv"
                return response
            else:
                return Response(result, 200)
    except Exception as e:
        return Response(str(e), 500)

    try:
        if phone is not None:
            phones = [phone]
            result += process_results(bf, es.search_es(
                ElasticSearchManager.create_terms_query(phone_field, phones), int(size)))

            if store == "1":
                response = make_response(result)
                response.headers["Content-Disposition"] = "attachment; filename=data.tsv"
                return response
            else:
                return Response(result, 200)
    except Exception as e:
        return Response(str(e), 500)


@application.route('/api/ads/bulk-query', methods=['POST'])
@requires_basic_auth
def process_csv():
    try:
        json_data = json.loads(str(request.get_data()))
        esm = ElasticSearchManager()
        print json_data
        es_request = convert_csv_to_esrequest(json_data['csv'])

        size = request.args.get('size')
        headings = request.args.get('heading')
        store = request.args.get('store')

        if size is None:
            size = '20'

        if headings is None:
            headings = '0'

        if store is None:
            store = '1'

        bf = BulkFolders()

        if headings == "1":
            result = "\t".join(bf.ht_headings) + '\n'
        else:
            result = ''

        print result

        if 'ids' in es_request:
            result += process_results(bf, esm.search_es(ElasticSearchManager.create_ids_query
                                                        (es_request['ids']), len(es_request['ids'])))
        if 'phone' in es_request:
            result += process_results(bf,
                                      esm.search_es(ElasticSearchManager.create_terms_query(phone_field,
                                                    es_request['phone']), int(size)))
        if store == "1":
            response = make_response(result)
            response.headers["Content-Disposition"] = "attachment; filename=data.tsv"
            return response
        else:
            return Response(result, 200)
    except Exception as e:
        return Response(str(e), 500)


"""folder_name = _all for all folders"""
@application.route('/api/users/<user>/folders/<folder_name>/ads', methods=['GET'])
@requires_auth
def get_user_folders(user, folder_name):
    bf = BulkFolders()
    password = request.authorization.password
    print folder_name
    headings = request.args.get('heading')
    store = request.args.get('store')

    if store is None:
        store = '1'

    if headings is None:
            headings = '0'
    try:
        if store == "1":
            response = make_response(bf.construct_tsv_response(
                bf.dereference_uris(bf.construct_uri_to_folder_map(bf.get_folders(user, password), folder_name)), headings))
            response.headers["Content-Disposition"] = "attachment; filename=data.tsv"
            return response
        else:
            return Response(bf.construct_tsv_response(
                bf.dereference_uris(bf.construct_uri_to_folder_map(bf.get_folders(user, password))), headings), 200)
    except Exception as e:
        return Response(str(e), 500)


def process_results(bf, res):
    hits = res['hits']['hits']
    result = ''
    for hit in hits:
        ad = hit['_source']
        tab_separated = "\t".join(bf.ht_to_array(ad))
        result = result + tab_separated + '\n'
    return result[:result.rfind('\n')]


def convert_csv_to_esrequest(lines):

    es_request = {}
    ids = []
    phonenumbers = []

    # line is of format - uri,phonenumber etc
    for line in lines:
        data = line.split(',')

        if len(data) > 1 and data[0].strip() != '':
            ids.append(data[0])
        if len(data) > 1 and data[1].strip() != '':
            phonenumbers.append((data[1]))

    if len(ids) > 0:
        es_request["ids"] = ids
    if len(phonenumbers) > 0:
        es_request["phone"] = phonenumbers

    return es_request

if __name__ == "__main__":
    application.run()
