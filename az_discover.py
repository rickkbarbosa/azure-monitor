#!/bin/python3
#===============================================================================
# IDENTIFICATION DIVISION
#        ID SVN:   $Id$
#          FILE:  az_discovery.py
#         USAGE:  $0 
#   DESCRIPTION:  List in JSON-file Azure components
#                 -C "tenant_id,app_id,app_password,subscription_id": Send AZ credentials [unecessary when using environment variables]
#       OPTIONS:  -G Groupname (Usually Client Name). For inventary purposes
#                 --aks : List Kubernetes Clusters
#                 --virtualmachine : List VMs
#                 --datafactory
#                 --sql : List Database Servers
#                 --database "databaseserver_name,resource_group" : List all databases inside a specific database server
#                 --webapp: List all App Servers
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
parser.add_argument("--aks", dest="az_aks", help="AKS Clusters", action="store_true")
parser.add_argument("--connections", dest="az_connections", help="VPN Connections")
parser.add_argument("--virtualmachine", dest="az_vm", help="List VMs", action="store_true")
parser.add_argument("--datafactory", dest="az_datafactory", help="List DataFactory", action="store_true")
parser.add_argument("--sql", dest="az_sql", help="SQL Servers", action="store_true")
parser.add_argument("--database", dest="az_databases", help="SQL Databases")
parser.add_argument("--webapp", dest="az_webapp", help="WebApp", action="store_true")

parser.allow_interspersed_args = False
(options, args) = parser.parse_known_args()

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

    vm_list = list() 
    for vm in discover_result:
        details = vm.id.split("/")
      
        vm_detail = {'{#AZ_VM_NAME}': details[8],
                        '{#AZ_VM_RESOURCEGROUP}': details[4],
                        '{#AZ_VM_SUBSCRIPTIONS}': details[2],
                        '{#AZ_REGION}': vm.location,
                        '{#AZ_VM_GROUPNAME}': "{} - Azure".format(options.groupname)
                        }
        vm_list.append(vm_detail)
  
    print(json.dumps({"data": vm_list}, indent=4))

def azure_df_list():
    from azure.mgmt.datafactory import DataFactoryManagementClient
    
    compute_client = DataFactoryManagementClient(conn, subscription_id)
    discover_result = compute_client.factories.list()
    
    df_list = list()
    for df in discover_result:
        details = df.id.split("/")
      
        vm_detail = {'{#AZ_ADF_NAME}': details[8],
                        '{#AZ_ADF_RESOURCEGROUP}': details[4],
                        '{#AZ_ADF_SUBSCRIPTIONS}': details[2],
                        '{#AZ_REGION}': df.location,
                        '{#AZ_ADF_GROUPNAME}': "{} - Azure".format(options.groupname)
                        }
        df_list.append(vm_detail)
  
    print(json.dumps({"data": df_list}, indent=4))

def azure_webapp_list():
    from azure.mgmt.web import WebSiteManagementClient
    
    compute_client = WebSiteManagementClient(conn, subscription_id)
    discover_result = compute_client.web_apps.list()
    
    webapp_list = list()
    for web in discover_result:
        details = web.id.split("/")
      
        vm_detail = {'{#AZ_WEBAPP_NAME}': details[8],
                        '{#AZ_WEBAPP_RESOURCEGROUP}': details[4],
                        '{#AZ_WEBAPP_SUBSCRIPTIONS}': details[2],
                        '{#AZ_REGION}': web.location,
                        '{#AZ_WEBAPP_GROUPNAME}': "{} - Azure".format(options.groupname)
                        }
        webapp_list.append(vm_detail)
  
    print(json.dumps({"data": webapp_list}, indent=4))

def azure_sql_instances_list():
    from azure.mgmt.sql import SqlManagementClient
    
    compute_client = SqlManagementClient(conn, subscription_id)
    discover_result = compute_client.servers.list()
    
    db_list = list()
    for db in discover_result:
        details = db.id.split("/")
      
        vm_detail = {'{#AZ_DBSERVER_NAME}': details[8],
                        '{#AZ_DBSERVER_RESOURCEGROUP}': details[4],
                        '{#AZ_DBSERVER_SUBSCRIPTIONS}': details[2],
                        '{#AZ_REGION}': db.location,
                        '{#AZ_DBSERVER_GROUPNAME}': "{} - Azure".format(options.groupname)
                        }
        db_list.append(vm_detail)
  
    print(json.dumps({"data": db_list}, indent=4))

def azure_databases_list(instance_name, resource_group):
    from azure.mgmt.sql import SqlManagementClient
    
    rg_name = resource_group
    server_name = instance_name

    compute_client = SqlManagementClient(conn, subscription_id)
    discover_result = compute_client.databases.list_by_server(resource_group_name=rg_name, 
                                                             server_name=server_name)
    
    db_list = list()
    for web in discover_result:
        details = web.id.split("/")
      
        vm_detail = {'{#AZ_DATABASE_NAME}': details[10],
                    '{#AZ_DATABASESERVER_NAME}': details[8],
                        '{#AZ_DATABASE_RESOURCEGROUP}': details[4]
                        }
        db_list.append(vm_detail)
  
    print(json.dumps({"data": db_list}, indent=4))
    
def azure_connection_list(connection):
    from azure.mgmt.resource import ResourceManagementClient
    from azure.mgmt.network import NetworkManagementClient
    
    ''' First, list the resource groups'''
    rg_client = ResourceManagementClient(conn, subscription_id)
    compute_client = NetworkManagementClient(conn, subscription_id)

    rg_result = rg_client.resource_groups.list()
    connection_list = list()
    discover_result = ()

    for rg in rg_result:
        rg_name = rg.id.split("/")[4]

        ''' Then, start a conection research, once per resource group '''

        ''' Discovers Application Gateway '''
        if (connection == "app_gateway" ):
            discover_result = compute_client.application_gateways.list(resource_group_name=rg_name)
        else:
            ''' Discovers VPN Gateway '''
            discover_result = compute_client.virtual_network_gateway_connections.list(resource_group_name=rg_name)

        for connection in discover_result:
            details = connection.id.split("/")
        
            vm_detail = {'{#AZ_CONN ECTION_NAME}': details[8],
                            '{#AZ_CONNECTION_RESOURCEGROUP}': details[4],
                            '{#AZ_REGION}': connection.location,
                            '{#AZ_CONNECTION_SUBSCRIPTIONS}': details[2],
                            }
            connection_list.append(vm_detail)
  
    print(json.dumps({"data": connection_list}, indent=4))

def azure_aks_list():
    from azure.mgmt.containerservice import ContainerServiceClient
    
    ''' First, list the resource groups'''
    compute_client = ContainerServiceClient(conn, subscription_id)

    kubernetes_list = list()

    ''' Then, start a conection research, once per resource group '''
    discover_result = compute_client.managed_clusters.list()
    for kubernetes_cluster in discover_result:
        details = kubernetes_cluster.id.split("/")
    
        vm_detail = {'{#AZ_AKS_NAME}': details[8],
                        '{#AZ_AKS_RESOURCEGROUP}': details[4],
                        '{#AZ_AKS_SUBSCRIPTIONS}': details[2],
                        '{#AZ_REGION}': kubernetes_cluster.location,
                        '{#AZ_AKS_GROUPNAME}': "{} - Azure".format(options.groupname)
                        }
        kubernetes_list.append(vm_detail)
  
    print(json.dumps({"data": kubernetes_list}, indent=4))

''' For menu '''
def main(credentials):
    get_credentials(credentials=credentials)

    if (options.groupname == None):
        options.groupname = 'Discovered Hosts'

    if (options.az_datafactory):
        azure_df_list()
    
    if (options.az_connections):
        az_connections_options = ''.join(str(e) for e in options.az_connections)
        azure_connection_list(connection=az_connections_options)

    if (options.az_vm):
        azure_vm_list()

    if (options.az_webapp):
        azure_webapp_list()

    if (options.az_sql):
        azure_sql_instances_list()

    if (options.az_aks):
        azure_aks_list()

    if (options.az_databases):
       
        az_databases_options = options.az_databases.split(',')
        if len(az_databases_options) <2:
                print("USAGE: sql_instance_name, resource_group")
                sys.exit(1)
        else:
            sql_instance = az_databases_options[0]
            resource_group = az_databases_options[1]
            azure_databases_list(instance_name=sql_instance, resource_group=resource_group)

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