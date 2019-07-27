#!/usr/bin/python3

import click
import requests
import json 
import datetime
import hashlib
import hmac
import pandas
import base64
import codecs
import sys

# Block needed to debug HTTP requests in Python3
import logging 
import http.client as http_client

#http_client.HTTPConnection.debuglevel = 1
# You must initialize logging, otherwise you'll not see debug output.
#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)
#requests_log = logging.getLogger("requests.packages.urllib3")
#requests_log.setLevel(logging.DEBUG)
#requests_log.propagate = True
# End Block needed

ERR = '\033[1;40;41m'
EEND = '\033[0m'
ATT = '\033[92m'
AEND = '\033[00m'
def prError(msg): print(f"{ERR}{msg}{EEND}")
def prAttn(msg): print(f"{ATT}{msg}{AEND}")

# Build and send a request to the POST API
def get_log_analytics(add, token, workspace_id, kql, timespan):
    #print(body)
    #uri=f"{add}/{workspace_id}/api/query?api-version=2017-01-01-preview"
    uri=f"https://api.loganalytics.io/v1/workspaces/{workspace_id}/query"
    method = 'POST'
    content_type = 'application/json'

    headers = {   
        f"Content-Type":f"application/json",
        f"Authorization":f"Bearer {token}"
    }

    body = {
        f"query": f"{kql}",
        f"timespan": f"{timespan}"
    }

    response = requests.post(uri, headers=headers, data=json.dumps(body))
    if response.status_code != 200:
        print(f"Response code: {response.status_code}")
        err_msg = json.loads(response.text)
        prError(f"FULL ERROR MESSAGE: {err_msg}")
        raise ValueError("ERROR: Failure has occurred.  Check error message above.")
    return response.json()

def get_token(add, resource, tenant_id, client_id, secret_key ):
    url = f"{add}/{tenant_id}/oauth2/token"
    grant_type=f"client_credentials"
    resource=f"{resource}"
    body = {
        f"grant_type":f"{grant_type}",
        f"client_id":f"{client_id}",
        f"client_secret":f"{secret_key}",
        f"resource":f"{resource}"
    }
    response = requests.post(url, data=body)
    data=response.json()
    return data["access_token"]


def get_query_data(filename):
    with open(filename) as f: 
        data = f.read() 
    return data

@click.command()
@click.argument('query_file',
    type=click.Path(exists=True),
    required=False
)
@click.option('--timespan', '-t',
    default='P1DTH',
    required=True,
    help='Time period the query should span'
)
@click.option('--azure_auth', '-a', 
    type=click.Path(exists=True), 
    required=True, 
    envvar='AZURE_AUTH_LOCATION', 
    help='Azure auth file formated in JSON'
)
@click.option('--output', '-o',
    type=click.Choice(['table', 'json', 'csv', 'standard']),
    default=('table'), 
    help='Type of output to produce'
)
@click.option('--workspace_id', '-w',
    required=True,
    envvar='LOG_ANALYTICS_WORKSPACE_ID',
    help="Name of Log Analytics workspace to query"
)
@click.option('--debug', '-d',
    default=False, 
    is_flag=True, 
    help='Boolean flag that turns on additional output'
)

def main(query_file, azure_auth, timespan, output, debug, workspace_id):
    """
    A little tool that queries Log Analytics via REST API calls.  Also see az monitor log-analytics 
    for similar capabilities.  The biggest difference being that this will accept stdin as well as
    produce formatted reports.
    """
    kql_data = None
    if not query_file:
        kql_data = sys.stdin.read()
    else:    
        kql_data = get_query_data(query_file)


    if not kql_data:
        raise ValueError("Where is my KQL?")

    # Grab the auth from a service principal defined in json using...
    # az ad sp create-for-rbac --sdk-auth > .azureauth
    # This can be passed in as an argument or set via AZURE_AUTH_LOCATION env var
    with open(azure_auth, "r") as json_file:
        auth_info = json.load(json_file)

    # Notice below that the https://api.loganalytics.io resource is passed in.  This
    # will create a Bearer Token capable of querying Log Analytics.  If you use the 
    # standard ARM endpoint you will not be able to authenticate against Log Analytics
    bearer_token = get_token(
            auth_info["activeDirectoryEndpointUrl"], 
            #auth_info["resourceManagerEndpointUrl"],
            f"https://api.loganalytics.io",
            auth_info["tenantId"], 
            auth_info["clientId"], 
            auth_info["clientSecret"]
        )
    
    data = get_log_analytics(
            auth_info["resourceManagerEndpointUrl"],
            bearer_token, 
            workspace_id, 
            kql_data, 
            timespan
        )

    # Setup pandas DataFrame so we get the format we want
    columns_array=(data['tables'][0]['columns'])
    columns=[x['name'] for x in columns_array]
    rows=(data['tables'][0]['rows'])

    df = pandas.DataFrame(rows, columns=columns)

    if output == 'json':
        print(df.to_json(orient='records'))
    elif output == 'csv':
        print(df.to_csv(index=False))
    elif output == 'standard':
        print(json.dumps(data))
    else:
        prAttn("====================================================================")
        print(f"KQL:")
        prAttn(f"{kql_data}")
        prAttn("====================================================================")
        print(df.to_string(index=False))





if __name__ == "__main__":
    main()
