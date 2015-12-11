import json
from httplib import HTTPSConnection
from base64 import b64encode
import ConfigParser
from elasticsearch_manager import ElasticSearchManager
import codecs


class BulkFolders(object):

    def __init__(self):
        self.feature_names = [
            'person_ethnicity_feature',
            'phonenumber_feature',
            'place_postalAddress_feature',
            'provider_name_feature',
            'person_age_feature'
            ]

        self.ht_headings = [
            'hasIdentifier',
            'dateCrawled',
            'dateCreated',
            'dateModified',
            'url',
            'hasTitlePart',
            'hasBodyPart'
            ]
        self.ht_headings.extend(self.feature_names)

        configuration = ConfigParser.RawConfigParser()
        configuration.read('config.properties')
        self.bulkfoldersurl = configuration.get('BulkFolders', 'bulkapiurl')

    @staticmethod
    def get_feature_values(obj_or_array):
        """Given the values of a single feature, return them as a string.
        If the feature has a single calue we get an object. If it has
        multiple values we get an array and return the values separated with |."""
        # Possible fix needed here to convert the result to unicode instead of
        # using str()
        if isinstance(obj_or_array, list):
            result = "|".join(map(lambda x: str(x['featureValue']), obj_or_array))
        else:
            result = str(obj_or_array['featureValue'])
        if result is None:
            result = ''

        return result

    def get_feature_collection_values(self, fc):
        """Get the values of all features in feature collection fc."""
        result = []
        for x in self.feature_names:
            if x in fc:
                result.append(self.get_feature_values(fc[x]))
            else:
                result.append('')
        return result

    @staticmethod
    def stringify_value(value):
        """If value is a list, reduce to a string."""
        if isinstance(value, list):
            return "|".join(value)
        else:
            return value

    def ht_to_array(self, ht):
        """Create an array containing all the values we want to export from a
        WebPage object, ht."""

        identifier = ht.get('hasIdentifier', {})
        identifier_str = ''
        if isinstance(identifier, list):
            # identifier_str = "|".join(map(lambda x: x.get('label', ''), identifier_str))
            for ad_id in identifier:
                identifier_str = identifier_str + ad_id.get('label', '') + "|"
            identifier_str = identifier_str[0:len(identifier_str)-1]
        else:
            identifier_str = identifier.get('label', '')
        """
        body_text = ht.get('hasBodyPart', {}).get('text', '')
        # http://stackoverflow.com/questions/3224268/python-unicode-encode-error
        if type(body_text) == str:
            body = unicode(body_text, "utf-8", errors="ignore")
        else:
            body = unicode(body_text)
        body = body.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
        # I give up, the exported TSV file looks correct, Karma can import it
        # correctly, but it is messed up in Excel or Numbers
        """
        body = 'removed'

        result = [
            identifier_str,
            ht.get('dateCrawled', ''),
            ht.get('dateCreated', ''),
            ht.get('dateModified', ''),
            ht.get('url', ''),
            self.stringify_value(ht.get('hasTitlePart', {}).get('text', '')),
            body
        ]
        result.extend(self.get_feature_collection_values(ht['hasFeatureCollection']))
        return result

    @staticmethod
    def get_ads(uri_list):
        """Get a set of ads from an ES index.
        eg "els.istresearch.com:39200"
        """
        esm = ElasticSearchManager()
        results = esm.search_es(ElasticSearchManager.create_ids_query(uri_list), None)
        hits = results['hits']['hits']
        return map(lambda x: x['_source'], hits)

    @staticmethod
    def add_folder_to_uri_to_folder_map(folder, dictionary):
        """Add a folder to the uri_to_folder map."""
        name = folder['name']
        for item in folder['FolderItems']:
            uri = item['elasticId']
            entry = dictionary.get(uri, [])
            entry.append(name)
            dictionary[uri] = entry

    def construct_uri_to_folder_map(self, folder_list):
        """Convert a list of folders into a dictionary {uri: [folders]}"""
        uri_to_folders_map = {}
        for folder in folder_list:
            self.add_folder_to_uri_to_folder_map(folder, uri_to_folders_map)
        return uri_to_folders_map

    def dereference_uris(self, dictionary):

        result = []
        ads = self.get_ads(dictionary.keys())
        for ad in ads:
            folders_names = dictionary[ad['uri']]
            tab_separated = '|'.join(folders_names) + '\t' + "\t".join(self.ht_to_array(ad))

            result.append(tab_separated)

        return result

    def get_folders(self, username, password):
        """Return JSON array of folder contents"""

        credentials = username + ":" + password
        conn = HTTPSConnection(self.bulkfoldersurl)
        userandpass = b64encode(credentials).decode("ascii")
        headers = {
            'cache-control': "no-cache",
            'Authorization': 'Basic %s' % userandpass
        }

        conn.request("GET", "/api/users/" + username + "/folders", headers=headers)

        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))

    def format_tsv_lines(self, lines):
        """Write the lines to standard output.
        This does not work because of the following error:
          UnicodeEncodeError:
          'ascii' codec can't encode characters in position 150-151:
          ordinal not in range(128)
        Apparently the problem is that the console cannot display it,
        but it is OK to put in a file.
        The write_tsv file will work correctly.
        """
        print('folder\t' + '\t'.join(self.ht_headings))
        for line in lines:
            print(line)

    def construct_tsv_response(self, lines):
        self.write_tsv('folder_export.tsv', lines)
        tsv_response = 'folder\t' + '\t'.join(self.ht_headings)+'\n'
        tsv_response += '\n'.join(lines)
        return tsv_response

    def write_tsv(self, file_name, lines):
        """Write the lines for each ad to a file."""
        out_file = codecs.open(file_name, "w", "utf-8")
        out_file.write('folder\t' + '\t'.join(self.ht_headings)+'\n')
        out_file.write('\n'.join(lines))
        out_file.close()
