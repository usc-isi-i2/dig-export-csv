import json
from http.client import HTTPSConnection
from base64 import b64encode
import codecs

feature_names = [
    'person_ethnicity_feature',
    'phonenumber_feature',
    'place_postalAddress_feature',
    'provider_name_feature',
    'person_age_feature'
]


def get_feature_values(obj_or_array):
    """Given the values of a single feature, return them as a string.
    If the feature has a single calue we get an object. If it has
    multiple values we get an array and return the values separated with |."""
    # Possible fix needed here to convert the result to unicode instead of
    # using str()
    result = ''
    if isinstance(obj_or_array, list):
        result = "|".join(map(lambda x: str(x['featureValue']), obj_or_array))
    else:
        result = str(obj_or_array['featureValue'])
    if result is None:
        result = ''

    return result


def get_feature_collection_values(fc):
    """Get the values of all features in feature collection fc."""
    result = []
    for x in feature_names:
        if (x in fc):
            result.append(get_feature_values(fc[x]))
        else:
            result.append('')
    return result


ht_headings = [
    'hasIdentifier',
    'dateCrawled',
    'dateCreated',
    'dateModified',
    'url',
    'hasTitlePart',
    'hasBodyPart'
]
ht_headings.extend(feature_names)


def stringify_value(value):
    "If value is a list, reduce to a string."
    if isinstance(value, list):
        return "|".join(value)
    else:
        return value


def ht_to_array(ht):
    """Create an array containing all the values we want to export from a
    WebPage object, ht."""
    identifier = ht.get('hasIdentifier', {})
    identifier_str = ''
    if isinstance(identifier, list):
        identifier_str = "|".join(
            map(lambda x: x.get('label', ''), identifier_str))
    else:
        identifier_str = identifier.get('label', '')

    body_text = ht.get('hasBodyPart', {}).get('text', '')
    # http://stackoverflow.com/questions/3224268/python-unicode-encode-error
    if type(body_text) == str:
        body = unicode(body_text, "utf-8", errors="ignore")
    else:
        body = unicode(body_text)
    body = body.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
    # I give up, the exported TSV file looks correct, Karma can import it
    # correctly, but it is messed up in Excel or Numbers
    #body = 'removed'

    result = [
        identifier_str,
        ht.get('dateCrawled', ''),
        ht.get('dateCreated', ''),
        ht.get('dateModified', ''),
        ht.get('url', ''),
        stringify_value(ht.get('hasTitlePart', {}).get('text', '')),
        body
    ]
    result.extend(get_feature_collection_values(ht['hasFeatureCollection']))
    return result


def get_ad(credentials, connection_url, uri):
    """Get an ad from an ES index.
    eg "els.istresearch.com:39200"
    """

    query = {
        "filter": {
            "term": {}
        }
    }
    query['filter']['term']['uri'] = uri

    conn = HTTPSConnection("dig.istresearch.com:5443")
    userAndPass = b64encode(credentials).decode("ascii")
    headers = {
        'cache-control': "no-cache",
        'Authorization': 'Basic %s' % userAndPass
    }

    conn.request(
        "POST",
        "/dig-latest/WebPage/_search",
        json.dumps(query),
        headers
    )
    res = conn.getresponse()
    data = res.read()

    object = json.loads(data.decode("utf-8"))
    return object['hits']['hits'][0]['_source']


def get_ads(credentials, connection_url, uri_list):
    """Get a set of ads from an ES index.
    eg "els.istresearch.com:39200"
    """
    query = {
        "filter": {
            "terms": {}
        }
    }
    query['size'] = len(uri_list)
    query['filter']['terms']['uri'] = uri_list
    conn = HTTPSConnection("dig.istresearch.com:5443")
    userAndPass = b64encode(credentials).decode("ascii")
    headers = {
        'cache-control': "no-cache",
        'Authorization': 'Basic %s' % userAndPass
    }

    conn.request(
        "POST",
        "/dig-latest/WebPage/_search",
        json.dumps(query),
        headers
    )
    res = conn.getresponse()
    data = res.read()

    results = json.loads(data.decode("utf-8"))
    # print(results)
    hits = results['hits']['hits']
    return map(lambda x: x['_source'], hits)


def add_folder_to_uri_to_folder_map(folder, dictionary):
    """Add a folder to the uri_to_folder map."""
    name = folder['name']
    for item in folder['FolderItems']:
        uri = item['elasticId']
        entry = dictionary.get(uri, [])
        entry.append(name)
        dictionary[uri] = entry


def construct_uri_to_folder_map(folder_list):
    """Convert a list of folders into a dictionary {uri: [folders]}"""
    uri_to_folders_map = {}
    for folder in folder_list:
        add_folder_to_uri_to_folder_map(folder, uri_to_folders_map)
    return uri_to_folders_map


def dereference_uris(credentials, connection_url, dictionary):
    """"""
    result = []
    ads = get_ads(credentials, connection_url, dictionary.keys())
    for ad in ads:
        folders_names = dictionary[ad['uri']]
        tab_separated = '|'.join(folders_names) + '\t' + "\t".join(ht_to_array(ad))

        result.append(tab_separated)

    return result


def get_folders(credentials, host):
    """Return JSON array of folder contents"""

    conn = HTTPSConnection(host)
    userAndPass = b64encode(credentials).decode("ascii")
    headers = {
        'cache-control': "no-cache",
        'Authorization': 'Basic %s' % userAndPass
    }

    conn.request("GET", "/api/users/txdps/folders", headers=headers)

    res = conn.getresponse()
    data = res.read()

    return json.loads(data.decode("utf-8"))


def format_tsv_lines(lines):
    """Write the lines to standard output.
    This does not work because of the following error:
      UnicodeEncodeError:
      'ascii' codec can't encode characters in position 150-151:
      ordinal not in range(128)
    Apparently the problem is that the console cannot display it,
    but it is OK to put in a file.
    The write_tsv file will work correctly.
    """
    print('folder\t' + '\t'.join(ht_headings))
    for line in lines:
        print(line)


def write_tsv(file_name, lines):
    "Write the lines for each ad to a file."
    file = codecs.open(file_name, "w", "utf-8")
    file.write('folder\t' + '\t'.join(ht_headings)+'\n')
    file.write('\n'.join(lines))


write_tsv(
    'folder_export.tsv',
    dereference_uris(
        'login:password!',
        'dig.istresearch.com:5443',
        construct_uri_to_folder_map(get_folders(
            'login:password',
            'dig.istresearch.com:5443'))))

