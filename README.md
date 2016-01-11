# dig-export-csv

##Prerequisites
Install virtualenv  
Open a terminal, type  
```pip install virtualenv```

##Setup
Open a terminal,  
1. ```git clone https://github.com/usc-isi-i2/dig-export-csv.git```  
2. ```cd dig-export-csv```  
3. ```virtualenv venv```  
4. ```. venv/bin/activate```  
5. ``` pip install flask```  
6. ```pip install elasticsearch```  
7. ```pip install requests```  

##Running the webservice   
In a terminal, type   
```python application.py```  
You should see a message  
``` * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)```  

##API    
###GET /api/users/\<user\>/folders/<folder_name>/ads  
Retrieves the ads for a given user from all folders.

**Method:** GET

**Basic Authentication:** YES

**Parameters:**

| Parameter | Description | Required |
| --------- | ----------- | -------- |
| user  | dig user name | Yes |
| folder_name  | folder name from which to get the ads from, _all for all folders | Yes |
| heading  | 1 to get the column names as first line, by default 0  | No |
| store  | 1 to download the file as data.tsv, by default 1  | No |

**Example:**
```      
curl -u <username>:<password> localhost:5000/api/users/memex/folders/_all/ads?heading=1&store=1
```   
```
curl -u <username>:<password> localhost:5000/api/users/memex/folders/December%20HT/ads?heading=1&store=1
```
###GET /api/ads?post_ids='id1,id2,id3'
Retrieves the ads that contain the given post ids in the url of the ad

**Method:** GET

**Basic Authentication:** YES

**Parameters:**

| Parameter | Description | Required |
| --------- | ----------- | -------- |
| post_ids  | comma separated string of post ids | Yes |
| size  | number of ads returned per post id, default = 20 | No |
| heading  | 1 to get the column names as first line, by default 0  | No |
| store  | 1 to download the file as data.tsv, by default 1  | No |

**Example:**
```      
curl -u <username>:<password> localhost:5000/api/ads?post_ids='20212377,20212378&size=40&heading=1'
```   
###GET /api/ads?uri='a uri goes here'
Retrieve the ad that has the given URI

**Method:** GET

**Basic Authentication:** YES

**Parameters:**

| Parameter | Description | Required |
| --------- | ----------- | -------- |
| uri  | uri of the ad as indexed in ElasticSearch | Yes |
| heading  | 1 to get the column names as first line, by default 0  | No |
| store  | 1 to download the file as data.tsv, by default 1  | No |

**Example:**
```      
curl -u <username>:<password> 'localhost:5000/api/ads?uri=http://dig.isi.edu/ht/data/page/47561AE61432324E428A67DA4763EAA1DB1809F7/1440921440000/processed&heading=1'
```
###GET api/ads?phone='a phone goes here'
Retrieve all the ads that contain the given phone.

**Method:** GET

**Basic Authentication:** YES

**Parameters:**

| Parameter | Description | Required |
| --------- | ----------- | -------- |
| phone  | phone number to be searched in ads | Yes |
| size  | number of ads returned, default = 20 | No |
| heading  | 1 to get the column names as first line, by default 0  | No |
| store  | 1 to download the file as data.tsv, by default 1  | No |

**Example:**
```      
curl -u <username>:<password> 'localhost:5000/api/ads?phone=8104496460&heading=1&store=1'
```
###POST api/ads/bulk-query
Fetch the ads that satisfy the query given in the body. The query consists of a CSV file with a spec per line. The spec contains headings such as URI, phone.

**Method:** POST

**Basic Authentication:** YES

**Parameters:**

| Parameter | Description | Required |
| --------- | ----------- | -------- |
| csv  | lines in the format uri,phone | Yes |
| size  | number of ads returned matching phone numbers, default = 20 | No |
| heading  | 1 to get the column names as first line, by default 0  | No |
| store  | 1 to download the file as data.tsv, by default 1  | No |

**Example:**
```      
curl -X POST -u <username>:<password>  localhost:5000/api/ads/bulk-query?heading=1 -d '{"csv":["http://dig.isi.edu/ht/data/page/47561AE61432324E428A67DA4763EAA1DB1809F7/1440921440000/processed,8104496460"]}'
```
