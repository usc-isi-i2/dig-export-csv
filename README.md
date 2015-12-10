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
```python process_request.py```  
You should see a message  
``` * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)```  

##API    
###/export/username
```      
Request Type : POST    
Parameters : {"password":""}    
Example run : python tests/test_folder_names.py
```   
###/export/postids
```
Request Type : POST    
Parameters : {"postids":"20212377","size":"20"}   
Example run : python tests/test_export_postids.py
```   
###/export/csv
```  
Request Type : POST    
Parameters : {"csv":lines,"size":"40"}  
Example run : python tests/test_input_csv.py  
```  
where lines is of the format 'uri,phonenumber' , sample in tests/test_input.csv




