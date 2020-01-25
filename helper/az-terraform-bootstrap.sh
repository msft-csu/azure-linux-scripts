#!/bin/bash

set -o errexit  # exit if any statement returns a non-true return value

usage() { 
    echo "`basename $0`"
    echo "   Usage: " 
    echo "     [-g <group>] resource group to use. tfstate-rg is the default"
    echo "     [-r <region>] region to use. EastUs or USGovVirginia are defaults"
    echo "     [-s <storageacct-name>] storage account name to use. tfstate-sa is the default."
    echo "     [-c <container-name>] container name to use. tfstate is the default."
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

while getopts g:c:s:r: option
do
    case "${option}"
    in
        g) RESOURCE_GROUP_NAME=${OPTARG};;
        r) REGION=${OPTARG};;
        c) CONTAINER_NAME=${OPTARG};;
        a) STORAGE_ACCOUNT_NAME=${OPTARG};;
        *) usage;;
        : ) usage;;
    esac
done
shift "$(($OPTIND -1))"

# Check if Region is passed in, otherwise eastus will be used
if [ -z "$REGION" ]; then
    # check if in gov or commercial
    CLOUD=`az account list-locations -o json | jq -r '.[0].name'`
    if [ ${CLOUD:0:5} = "usgov" ]; then
        REGION='usgovvirginia'
    else
        REGION='eastus'
    fi
fi

if [ -z "$RESOURCE_GROUP_NAME" ]; then
    RESOURCE_GROUP_NAME=tfstate
fi

if [ -z "$STORAGE_ACCOUNT_NAME" ]; then
    STORAGE_ACCOUNT_NAME=tfstate$RANDOM
fi

if [ -z "$CONTAINER_NAME" ]; then
    CONTAINER_NAME=tfstate
fi

# Create resource group
az group create --name $RESOURCE_GROUP_NAME --location $REGION

# Create storage account
az storage account create --resource-group $RESOURCE_GROUP_NAME --name $STORAGE_ACCOUNT_NAME --sku Standard_LRS --encryption-services blob

# Get storage account key
ACCOUNT_KEY=$(az storage account keys list --resource-group $RESOURCE_GROUP_NAME --account-name $STORAGE_ACCOUNT_NAME --query [0].value -o tsv)

# Create blob container
az storage container create --name $CONTAINER_NAME --account-name $STORAGE_ACCOUNT_NAME --account-key $ACCOUNT_KEY

echo "storage_account_name: $STORAGE_ACCOUNT_NAME"
echo "container_name: $CONTAINER_NAME"
echo "access_key: $ACCOUNT_KEY"
