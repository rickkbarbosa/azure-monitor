#!/bin/bash
#===============================================================================
# IDENTIFICATION DIVISION
#        ID SVN:   $Id$
#          FILE:  azure_monitor_vpn.sh 
#         USAGE:  $0 "<TENANT_ID>:APP_ID:PASSWORD:RESOURCE_GROUP" -d or -s
#   DESCRIPTION:  AZ VPNGateway status monitor
#       OPTIONS:  --- 
#  REQUIREMENTS:  azure-cli (https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
#                 jq (apt install jq) 
#          BUGS:  --- 
#         NOTES:  --- 
#          TODO:  --- 
#        AUTHOR:  Marcio Garcia, marcio.garcia@la.logicalis.com 
#       COMPANY:  Logicalis
#       VERSION:  1.0 
#       CREATED:  2020-Jan-07 08:00 AM BRT 
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

vpn_status() {
  VPN_CONN_NAME=${1}
  az network vpn-connection show --name ${VPN_CONN_NAME} --resource-group ${RESOURCE_GROUP} | jq -r '.connectionStatus'
}

#BEGIN
while getopts "c:ds:" parameter; do
    case "${parameter}" in
      c)
         export AZURE_CREDENTIALS=${OPTARG}
        ;;
      d)
          azure_login
          vpn_discover
          ;;
      s)
          azure_login
          vpn_status ${OPTARG} ;
          ;;
    esac
done

shift $((OPTIND-1))