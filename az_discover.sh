#!/bin/bash
#===============================================================================
# IDENTIFICATION DIVISION
#        ID SVN:   $Id$
#          FILE:  az_discover.sh 
#         USAGE:  $0 -C "<TENANT_ID>:APP_ID:PASSWORD:RESOURCE_GROUP" -d or -s
#   DESCRIPTION:  AZ items discovery - Add-on for what az_discover.py could not research
#       OPTIONS:  -a: Discovers API Managements
#                 -d : discovers Azure databricks
#                 -v: discovers VPN Gateway 
#  REQUIREMENTS:  azure-cli (https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
#                 jq (apt install jq) 
#          BUGS:  --- 
#         NOTES:  --- 
#          TODO:  --- 
#        AUTHOR:  Ricardo Barbosa, rickkbarbosa@live.com
#       COMPANY:  ---
#       VERSION:  1.0 
#       CREATED:  2021-Ago-24 12:58 PM BRT
#      REVISION:  ---
#=============================================================================== 

azure_login() {
  # Tenant ID for your Azure subscription
  TENANT_ID=$(echo ${AZURE_CREDENTIALS} | cut -d \: -f 1;)
  # Your service principal App ID
  APP_ID=$(echo ${AZURE_CREDENTIALS} | cut -d \: -f 2;)
  # Your service principal password
  PASSWORD=$(echo ${AZURE_CREDENTIALS} | cut -d \: -f 3;)
  #The resource group
  RESOURCE_GROUP=$(echo ${AZURE_CREDENTIALS} | cut -d \: -f 4;)

  az login --service-principal --username ${APP_ID} --password ${PASSWORD} --tenant ${TENANT_ID} >/dev/null
}


usage() {
  echo "Usage: $0 -ds 

        -d         Discover all VPN Gateways on the refered account
        -s [VPN_GATEWAY_NAME]         Dislays the Status from referred VPN Gateway, ingressBytesTransferred and egressBytesTransferred 
        "
   1>&2; exit 1;
}

vpn_discover() {
  VPN_LIST=$(az network vpn-connection list --resource-group ${RESOURCE_GROUP} | grep name;)
  IFS=,
  echo -n '{"data":['
  for VPN_GATEWAY in $VPN_LIST; do
    VPN_GATEWAY=$(echo ${VPN_GATEWAY}  | awk '{print $2}' | tr -d ',')
    #echo -n "$VPN_GATEWAY"
    echo -n "{\"{#VPN_GATEWAY_NAME}\": $VPN_GATEWAY },"
  done  |sed -e 's:\},$:\}:'

  echo -n ']}' 
}

apim_discover() {
  APIM_LIST=$(az apim list | grep '"id"' | awk '{print $2}')
  #IFS=,
  echo -n '{"data":['
  for APIM in $APIM_LIST; do
    APIM_NAME=$(echo $DATABRICKS | cut -d '/' -f 9 | tr -d  '",')
    APIM_RESOURCE_GROUP=$(echo $DATABRICKS | cut -d '/' -f 5)
    #echo -n "$VPN_GATEWAY"
    echo -n "{\"{#DATABRICKS_NAME}\": \"${APIM_NAME}\" , \"{#DATABRICKS_RESOURCE_GROUP}\": \"${APIM_RESOURCE_GROUP}\" },"
  done  |sed -e 's:\},$:\}:'

  echo -n ']}' 
}

databricks_discover() {
  ADB_LIST=$(az databricks workspace list | grep '"id"' | awk '{print $2}')
  #IFS=,
  echo -n '{"data":['
  for DATABRICKS in $ADB_LIST; do
    DATABRICKS_NAME=$(echo $DATABRICKS | cut -d '/' -f 9 | tr -d  '",')
    DATABRICKS_RESOURCE_GROUP=$(echo $DATABRICKS | cut -d '/' -f 5)
    #echo -n "$VPN_GATEWAY"
    echo -n "{\"{#DATABRICKS_NAME}\": \"${DATABRICKS_NAME}\" , \"{#DATABRICKS_RESOURCE_GROUP}\": \"${DATABRICKS_RESOURCE_GROUP}\" },"
  done  |sed -e 's:\},$:\}:'

  echo -n ']}' 
}

vpn_status() {
  VPN_CONN_NAME=${1}
  az network vpn-connection show --name ${VPN_CONN_NAME} --resource-group ${RESOURCE_GROUP} | jq -r '.connectionStatus'
}

#BEGIN
while getopts "C:adv:" parameter; do
    case "${parameter}" in
      C)
         export AZURE_CREDENTIALS=${OPTARG}
        ;;
      v)
          azure_login
          vpn_discover
          ;;
      a)
          azure_login
          apim_discover
          ;;   
      d)
          azure_login
          databricks_discover
          ;;
    esac
done

shift $((OPTIND-1))