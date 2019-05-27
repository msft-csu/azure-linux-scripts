## Azure Log Analytics.

### az-json-to-log-analytics

az-json-to-log-analytics will accept either a json file or json from stdin and load the data within the document into Log Analytics.  This can be useful in many situations where you want to load custom JSON data into Log Analytics.  For instance the following command would query a website and load the data into Log Analytics.

`curl https://jsonplaceholder.typicode.com/comments | az-json-to-log-analytics.py  -w "zzzzzzzzzzzzzzzzzz" -k "xxxxxxxxxxxxxxxxxxxxxxx" -l comments `

Where:  
  -w Log Analytics workspace id  
  -k Log Analytics key  
  -l Log Analytics record type  
  
  
You can also set environment variables instead of passing on the command line.  This script will accept the following:
  LOG_ANALYTICS_WORKSPACE_ID  
  AZURE_ANALYTICS_LOGTYPE  
  AZURE_ANALYTICS_KEY  
