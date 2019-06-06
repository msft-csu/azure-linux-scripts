#!/usr/bin/python3

import click
import requests
import json
import datetime
import hashlib
import hmac
import base64
import azure.keyvault
import azure.common.credentials
import pandas
import os
import codecs

# Block needed to debug HTTP requests in Python3
#import logging
#import http.client as http_client

#http_client.HTTPConnection.debuglevel = 1
# You must initialize logging, otherwise you'll not see debug output.
#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)
#requests_log = logging.getLogger("requests.packages.urllib3")
#requests_log.setLevel(logging.DEBUG)
#requests_log.propagate = True
# End Block needed

log_file_columns = [
                        "version-number",
                        "request-start-time",
                        "operation-type",
                        "request-status",
                        "http-status-code",
                        "end-to-end-latency-in-ms",
                        "server-latency-in-ms",
                        "authentication-type",
                        "requester-account-name",
                        "owner-account-name",
                        "service-type",
                        "request-url",
                        "requested-object-key",
                        "request-id-header",
                        "operation-count",
                        "requester-ip-address",
                        "request-version-header",
                        "request-header-size",
                        "request-packet-size",
                        "response-header-size",
                        "response-packet-size",
                        "request-content-length",
                        "request-md5",
                        "server-md5",
                        "etag-identifier",
                        "last-modified-time",
                        "conditions-used",
                        "user-agent-header",
                        "referrer-header",
                        "client-request-id"
                   ]

# Build the API signature
def build_signature(workspace_id, key, date, content_length, method, content_type, resource):
    x_headers = f"x-ms-date:{date}"
    string_to_hash = f"{method}\n{str(content_length)}\n{content_type}\n{x_headers}\n{resource}"
    bytes_to_hash=codecs.encode(string_to_hash, 'utf-8')
    decoded_key = base64.b64decode(key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest())
    authorization = f"SharedKey {workspace_id}:{encoded_hash.decode('utf-8')}"
    print(f"SharedKey: {authorization}")
    return authorization

# Build and send a request to the POST API
def post_to_log_analytics(workspace_id, key, body, log_type):
    print(body)
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(workspace_id, key, rfc1123date, content_length, method, content_type, resource)
    uri = f"https://{workspace_id}.ods.opinsights.azure.com{resource}?api-version=2016-04-01"

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }
    print(headers)

    response = requests.post(uri,data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        print(f"Accepted")
    else:
        print(f"Response code: {response.status_code}")

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
    #print(f"{data['access_token']}")
    return data["access_token"]

def get_file_data(filename):
    data = pandas.read_csv(filename,
        names=log_file_columns,
        delimiter=";"
    )
    json_data=data.to_json(orient='records')
    return json_data

def send_to_log_analytics(workspace_id, key, json_data, log_type):
    print(f"{workspace_id}")
    print(f"{key}")
    print(f"{json_data}")
    print(f"{log_type}")

@click.command()
@click.argument('ingestion_file',
    type=click.Path(exists=True)
)
@click.option('--workspace_id', '-w',
    required=True,
    envvar='AZURE_ANALYTICS_WORKSPACE_ID',
    help="Provide the Log Analytics Workspace ID"
)
@click.option('--azure_auth', '-a',
    type=click.Path(exists=True),
    required=True,
    envvar='AZURE_AUTH_LOCATION',
    help='Azure auth file formated in JSON'
)
@click.option('--key', '-k',
    required=True,
    envvar='AZURE_ANALYTICS_KEY',
    help="Provide the Log Analytics Shared Key"
)
@click.option('--debug', '-d',
    default=False,
    is_flag=True,
    help="Boolean flag that turns on additional output"
)
def main(ingestion_file, workspace_id, azure_auth, key, debug):
    """
    A little tool that writes data from a log file to Log Analytics via REST
    """
    with open(azure_auth, "r") as json_file:
        auth_info = json.load(json_file)

    tenant_id=auth_info["tenantId"]
    client_id=auth_info["clientId"]
    secret_key=auth_info["clientSecret"]
    json_data = get_file_data(ingestion_file)

    log_type = "StorageAccountAuditTest"

    post_to_log_analytics(workspace_id, key, json_data, log_type)

if __name__ == "__main__":
    main()
