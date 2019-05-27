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

### az-query-log-analytics
az-query-log-analytics takes a Kusto query (KQL) and passes it to the Log Analytics REST API.  It is NOT designed for large sets of data as it doesn't to break the return values up in any way.  What it does do though is make the return values useful.  The REST API for Log Analytics provides a network friendly JSON document that minimizes bandwidth by listing the column names seperately from the row data.  This produces much better network efficiency by reducing redundancy in the JSON at the cost of usefulness. This script will refactor the results into more useful formats like csv, table and verbose JSON.  You need to either pass a KQL file or pass it on stdin like so...

```bash 
python ~/external/bin/az-query-log-analtyics.py -t PT12H -w xxxxxxxxxxxxxxxx -a ~/.azureauth -o json <<EOF |  
Heartbeat  
| project Computer, OSType, OSMajorVersion  
| limit 2  
EOF  
jq 
```

This will produce a more verbose version of JSON that is more recognizable by folks.
```json
[  
  {  
    "Computer": "lin-7599",  
    "OSType": "Linux",  
    "OSMajorVersion": "18"  
  },  
  {  
    "Computer": "lin-7599",  
    "OSType": "Linux",  
    "OSMajorVersion": "18"  
  }  
]
```  
In addition to normal JSON you can also export csv and table formats of the Log Analytics data
```
Computer,OSType,OSMajorVersion
lin-7599,Linux,18
lin-7599,Linux,18
```
```
====================================================================
KQL:
Heartbeat
| project Computer, OSType, OSMajorVersion
| limit 2

====================================================================
 Computer OSType OSMajorVersion
 lin-7599  Linux             18
 lin-7599  Linux             18
 ```
