#!/bin/python3
#===============================================================================
# IDENTIFICATION DIVISION
#        ID SVN:   $Id$
#          FILE:  az_discovery.py
#         USAGE:  $0 
#   DESCRIPTION:  List in JSON-file Azure components
#                 -C "tenant_id,app_id,app_password,subscription_id": Send AZ credentials [unecessary when using environment variables]
#       OPTIONS:  -M "name,resource_group_name,type,metric_name": List available metrics for a item
#                 -m "name,resource_group_name,type,metric_name": Display Azure monitor metric value
#                 -G Groupname (Usually Client Name). For inventary purposes
#                 AVAILABLE TYPES: AKS, APIM, VM
#          BUGS:  ---
#         NOTES:  ---
#          TODO:  ---
#        AUTHOR:  Ricardo Barbosa, rickkbarbosa@live.com
#       COMPANY:  ---
#       VERSION:  1.0
#       CREATED:  2021-Ago-21 02:37 AM BRT
#      REVISION:  ---
#===============================================================================


import os, sys
import argparse
from azure.common.credentials import ServicePrincipalCredentials
import json


parser = argparse.ArgumentParser()
parser.add_argument("-C", "--credentials", dest="az_credentials", nargs=1, help="Declare AZ credentials [tenant_id,app_id,app_password,subscription_id]")
parser.add_argument("-G", "--groupname", dest="groupname", help="Maas Groupname")
parser.allow_interspersed_args = False
(options, args) = parser.parse_known_args()

''' Setting the right resource type '''
resource_type_list = {}
resource_type_list['AKS'] = "Microsoft.ContainerService/managedClusters"    #Kubernetes
resource_type_list['ADF'] = "Microsoft.DataFactory/factories"             #DataFactory
resource_type_list['APIM'] =  "Microsoft.ApiManagement/service"             #APIManagement
resource_type_list['VM'] = "Microsoft.Compute/virtualMachines"              #VM

def get_credentials(credentials):
    
    az_tenant_id = credentials[0]
    az_app_id = credentials[1]
    az_password = credentials[2]
    subscription_id = credentials[3]

    ''' Starting credential login '''
    credentials = ServicePrincipalCredentials(
        client_id = az_app_id,
        secret = az_password,
        tenant = az_tenant_id
    )

    #Conection itself
    global conn
    conn = credentials

    return conn, subscription_id


#List wich metrics is available for a Azure resource
def azure_vm_list():
    from azure.mgmt.compute import ComputeManagementClient
 
    compute_client = ComputeManagementClient(conn, subscription_id)

    discover_result = compute_client.virtual_machines.list_all()
    #print(vm_list)
    vm_list = list()
    
    for vm in discover_result:
        vm_details = vm.id.split("/")

        # ''' Getting VM State'''
        # try:
        #     vm_state = compute_client.virtual_machines.instance_view(vm_details[4], vm_details[8]).statuses
        #     vm_state = len(vm_state) >= 2 and vm_state[1]
        #     vm_state = vm_state.code.split("/")[1]
        # except:
        #     vm_state = "undefined"
        
        vm_detail = {'{#AZ_VM_NAME}': vm_details[8],
        #               '{#AZ_STATUS}': vm_state,
                        '{#AZ_VM_RESOURCEGROUP}': vm_details[4],
                        '{#AZ_VMSUBSCRIPTIONS}': vm_details[2],
                        '{#AZ_VM_GROUPNAME}': "{} - Azure".format(options.groupname)
                        }
        vm_list.append(vm_detail)
  
    print(json.dumps({"data": vm_list}, indent=4))


''' For menu '''
def main(credentials):
    get_credentials(credentials=credentials)
    azure_vm_list()

    if (options.groupname == None):
        options.groupname = 'Discovered Hosts'


if __name__ == '__main__':
    global subscription_id

    #''' Invoke credentials based on AZ Service Principal. Default is try to get system environment '''
    if (options.az_credentials != None):
        az_credentials_options = ''.join(str(e) for e in options.az_credentials)
        credentials = az_credentials_options.split(',')
        subscription_id = credentials[3]
    else:
        az_tenant_id = os.environ['AZ_TENANT_ID']
        az_app_id = os.environ['AZ_APP_ID']
        az_password = os.environ['AZ_APP_PASSWORD']
        subscription_id = os.environ['AZ_SUBSCRIPTION_ID']
        credentials = az_tenant_id, az_app_id, az_password, subscription_id
    ''' Open the party '''
    main(credentials=credentials)