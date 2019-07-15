#!/bin/bash 
# az-create-website - Author: Brent McConnell
# 
#
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# 
# Creates a website using an Azure Storage Acct in eastus... for now.

usage() { 
    echo "`basename $0`"
    echo "   Usage: " 
    echo "      -l <location>: Region for storage acct"
    echo "      -d <domain name>: domain name of website."
    echo "      -g <resource group>: Resource group."
    echo ""
    exit 1
}

# Catch any help requests
for arg in "$@"; do
  case "$arg" in
    --help| -h) 
        usage
        ;;
  esac
done

while getopts l:d:g: option
do
    case "${option}"
    in
        g) RG_NAME=${OPTARG};;
        t) DOMAIN=${OPTARG};;
        l) REGION=${OPTARG};;
        *) usage;;
        : ) usage;;
    esac
done
shift "$(($OPTIND -1))"

# Check if Resource Group has been passed in, if not we will create one
if [ -z "$RG_NAME" ]; then
    RG_NAME=RG-$RANDOM
else
    echo "Checking Existing Resource Group"
    EXISTING_RG=`az group show -g $RG -o json | jq -r '.name'`
    if [ -z "$EXISTING_RG" ]; then
        echo "Resource group passed in does not exist"
        exit 1 
    fi
fi

 Check if Region is passed in, otherwise eastus will be used
if [ -z "$REGION" ]; then
    REGION='eastus'
fi

if [[ $RG_NAME =~ ['!@#$%^&*()_+-'] ]]; then
  echo "ERROR:  Name cannot contain any special characters or dashes"
  exit 1
fi

# Check Which Cloud
WHICH_CLOUD=$(az cloud list --query "[].{Active:isActive, Name:name}[?Active==\`true\`]" -o tsv | awk '{print $2}')
echo "Running against $WHICH_CLOUD"

if [ -z "$AZURE_AUTH_LOCATION" ]; then
    echo "AZURE_AUTH_LOCATION not set.  Looking for .azureauth file in $HOME as fallback."
    if [ -f "$HOME/.azureauth" ]; then
        echo "Using $HOME/.azureauth for authenticating REST calls"
        AZURE_AUTH_LOCATION=$HOME/.azureauth
    fi
fi

if [ -z "$AZURE_AUTH_LOCATION" ]; then
    echo "ERROR: AZURE_AUTH_LOCATION env variable or .azureauth file not found."
    echo "       Use az ad sp create-for-rback --sdk-auth to create and store"
    exit 1
else
    if ! [ -f "$AZURE_AUTH_LOCATION" ]; then
        echo "$AZURE_AUTH_LOCATION does NOT exist. Ensure that AZURE_AUTH_ENVIRONMENT contains valid sp info"
        exit 1
    fi
fi

clientId=$(cat $AZURE_AUTH_LOCATION | jq -e -r 'select(.clientId != null) | .clientId')
subscriptionId=$(cat $AZURE_AUTH_LOCATION | jq -e -r 'select(.subscriptionId != null) | .subscriptionId')
tenantId=$(cat $AZURE_AUTH_LOCATION | jq -e -r 'select(.tenantId != null) | .tenantId')
secretKey=$(cat $AZURE_AUTH_LOCATION | jq -e -r 'select(.clientSecret != null) | .clientSecret')
activeDirectoryEndpoint=$(cat $AZURE_AUTH_LOCATION | jq -e -r 'select(.activeDirectoryEndpointUrl != null) | .activeDirectoryEndpointUrl')
resourceManagerEndpoint=$(cat $AZURE_AUTH_LOCATION | jq -e -r 'select(.resourceManagerEndpointUrl != null) | .resourceManagerEndpointUrl')
#echo $activeDirectoryEndpoint
#echo $resourceManagerEndpoint

if [ -z "$clientId" ]  || [ -z "$subscriptionId" ] || [ -z "$tenantId" ] || [ -z "$secretKey" ] ; then
    echo "File does not contain one or more of the following:"
    echo "clientId, subscriptionId, tenantId and/or clientSecret"
    exit 1
fi

function az-rg-exists() {
    EXISTING_RG=`az group show -g $RG_NAME -o json | jq -r '.name'`
    if [ -z "$EXISTING_RG" ]; then
        return 1 
    fi
    return 0
}

function az-sa-exists() {
    EXISTING_SA=`az storage account show -n $STOR_NAME -o json | jq -r '.name'`
    if [ -z "$EXISTING_SA" ]; then
        return 1
    fi
    return 0
}

function az-fa-exists() {
    EXISTING_FA=`az functionapp show -n $FUNC_NAME -g $RG_NAME -o json | jq -r '.name'`
    if [ -z "$EXISTING_FA" ]; then
        return 1
    fi
    return 0
}

if [ $WHICH_CLOUD == 'AzureCloud' ]; then
    TLD="net"
    REGION="eastus"
elif [ $WHICH_CLOUD == 'AzureUSGovernment' ]; then
    TLD="us"
    REGION="usgovvirginia"
else
    echo "Cloud Not Supported"
    exit 1
fi

RESP=$(curl -s -X POST \
    -d"grant_type=client_credentials&client_id=$clientId&client_secret=$secretKey&resource=$resourceManagerEndpoint" \
    $activeDirectoryEndpoint/$tenantId/oauth2/token)

TOKEN=$(echo $RESP | jq -r ".access_token")
#echo $TOKEN

if [ -z "$TOKEN" ]; then
    echo "Error: Failed to get AUTH Token for REST calls"
    exit 1
fi

echo "Sending HTTP POST Request to check Storage Acct resourcename............."
WEB_AVAILABLE=$(curl -s -S \
    -H "Content-Type: application/json; charset=UTF-8"\
    -H "Authorization: Bearer $TOKEN"\
    -XPOST $resourceManagerEndpoint/subscriptions/$subscriptionId/providers/Microsoft.Web/checkNameAvailability?api-version=2018-11-01 \
    -d'{
        "name": '\""$FUNC_NAME".azurewebsites."$TLD"\"',
        "isFQDN": true,
        "type": "Site"
    }' | jq -r ".nameAvailable") &> /dev/null || exit 1

if [ "$WEB_AVAILABLE" == "false" ]; then
    echo "Website Name Already Exists. Select another name"
    exit 1
fi


echo "Sending HTTP POST Request to Storage resourcename............."
SA_AVAILABLE=$(curl -s \
    -H "Content-Type: application/json; charset=UTF-8"\
    -H "Authorization: Bearer $TOKEN"\
    -XPOST $resourceManagerEndpoint/subscriptions/$subscriptionId/providers/Microsoft.Storage/checkNameAvailability?api-version=2018-11-01 \
    -d'{
        "Name": '\""$STOR_NAME"\"',
        "Type": "Microsoft.Storage/storageAccounts"
    }' | jq -r ".nameAvailable")

if [ "$SA_AVAILABLE" == "false" ]; then
    echo "Storage Account Already Exists. Select another name"
    exit 1
fi

if az-rg-exists $RG_NAME; then
    echo "Error: Resource Group Exists"
    exit 1
fi

if az-sa-exists $STOR_NAME; then
    echo "Error: Storage Acct Exists"
    exit 1
fi

if az-fa-exists $FUNC_NAME; then
    echo "Error: FunctionApp already exists"
fi


az group create \
    --name $RG_NAME \
    --location $REGION 1> /dev/null || exit 1

az storage account create \
    --name $STOR_NAME \
    --location $REGION \
    --resource-group $RG_NAME \
    --sku Standard_LRS 1> /dev/null || exit 1

echo "Storage Acct $STOR_NAME created successfully"

az functionapp create \
    --consumption-plan-location $REGION \
    --name $FUNC_NAME \
    --os-type $PLATFORM \
    --resource-group $RG_NAME \
    --runtime $RUNTIME \
    --storage-account $STOR_NAME 1> /dev/null || exit 1

echo "Function App $FUNC_NAME created successfully"

# Creates insights component for monitoring. Note generated instrumentation key
# is set in function app.
az resource create \
    --resource-group $RG_NAME \
    --resource-type "Microsoft.Insights/components" \
    --name $FUNC_NAME-ai \
    --location $REGION \
    --properties '{"Application_Type":"web"}' -o json \
| jq -r ".properties.InstrumentationKey" \
| xargs -I % az functionapp config appsettings set \
    --name $FUNC_NAME \
    --resource-group $RG_NAME \
    --settings "APPINSIGHTS_INSTRUMENTATIONKEY = %" || exit 1

echo "Application Insights configured"
