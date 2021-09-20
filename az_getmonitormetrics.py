#!/bin/python3 -W ignore
#===============================================================================
# IDENTIFICATION DIVISION
#        ID SVN:   $Id$
#          FILE:  get_azmonitordata.py
#         USAGE:  $0 
#   DESCRIPTION:  Get Azure Monitor metrics data using python
#                 -C "tenant_id,app_id,app_password,subscription_id": Send AZ credentials [unecessary when using environment variables]
#       OPTIONS:  -M "name,resource_group_name,type,metric_name": List available metrics for a item
#                 -m "name,resource_group_name,type,metric_name": Display Azure monitor metric value
#                 AVAILABLE TYPES: AKS, APIM, VM
#          BUGS:  ---
#         NOTES:  ---
#          TODO:  ---
#        AUTHOR:  Ricardo Barbosa, rickkbarbosa@live.com
#       COMPANY:  ---
#       VERSION:  1.0
#       CREATED:  2021-Ago-17 10:53 AM BRT
#      REVISION:  ---
#===============================================================================


#https://docs.microsoft.com/pt-br/python/api/overview/azure/monitoring?view=azure-python
#https://docs.microsoft.com/en-us/azure/azure-monitor/essentials/metrics-supported#microsoftkubernetesconnectedclusters
import os, sys
import argparse
import datetime
from azure.mgmt.monitor import MonitorManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from statistics import mean,fmean
import requests, json


parser = argparse.ArgumentParser()
parser.add_argument("-C", "--credentials", dest="az_credentials", nargs=1, help="Declare AZ credentials [tenant_id,app_id,app_password,subscription_id]")
parser.add_argument("-M", "--metric-list", dest="az_metric_list", nargs=1, help="List available metrics for a resource")
parser.add_argument("-m", "--metric", dest="az_metrics", nargs=1, help="Get metrics for a resource")
parser.add_argument("-t", "--timerange", dest="az_timerange", nargs=1, help="range to be get [in minutes]")
parser.allow_interspersed_args = False
(options, args) = parser.parse_known_args()

''' Setting the right resource type '''
resource_type_list = {}
resource_type_list['AKS'] = "Microsoft.ContainerService/managedClusters"    #Kubernetes
resource_type_list['ADF'] = "Microsoft.DataFactory/factories"             #DataFactory
resource_type_list['APIM'] =  "Microsoft.ApiManagement/service"             #APIManagement
resource_type_list['VM'] = "Microsoft.Compute/virtualMachines"              #VM
resource_type_list['WEB'] =  "Microsoft.Web/sites"                           #WebApp
#resource_type_list['DATABRICKS'] =  "Microsoft.Databricks/workspaces"                           #Databricks/Workspaces
resource_type_list['SQL'] =  "Microsoft.Sql/servers"
resource_type_list['CONNECTION'] =  "Microsoft.Network/"                      #Connections

azure_token_url = "login.microsoftonline.com"
monitoring_url = "management.azure.com"

def get_credentials(credentials):

    az_tenant_id = credentials[0]
    az_app_id = credentials[1]
    az_password = credentials[2]
    subscription_id = credentials[3]

    #global api_token
    token_url = "https://{}/{}/oauth2/token".format(azure_token_url, az_tenant_id)

    ''' Append needed headers to Login '''
    headers = {}
    headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36" 

    data = { "grant_type":"client_credentials",
             "client_id": az_app_id ,
             "client_secret": az_password
    }

    response = requests.post(token_url, headers=headers, data=data, timeout=10)
    
    if response.status_code == 200:
      api_token = json.loads(response.text)

    api_new_token = api_token['access_token']
    
    return api_new_token, subscription_id


''' Define timerange'''
''' minutes is keep as 5, but you could need different time ranges '''
def metrics_timerange(minutes=5):

    global timeto 
    global timetill

    timetill = datetime.datetime.utcnow()
    timeto = timetill - datetime.timedelta(minutes=minutes)

    return timeto, timetill


#List wich metrics is available for a Azure resource
def azmonitor_available_metrics(resource_name, resource_group, resource_type):
    ''' Identify the item '''
    resource_id = (
        "subscriptions/{}/"
        "resourceGroups/{}/"
        "providers/{}/{}"
    ).format(subscription_id, resource_group, resource_type_list[resource_type],  resource_name)

    for metric in client.metric_definitions.list(resource_id):
        print("{}: id={}, unit={}".format(
            metric.name.localized_value,
            metric.name.value,
            metric.unit
        ))


def get_az_metrics(resource_name, resource_group, resource_type, az_metric, metric_aggregation):
    # if api_new_token is None:
    #     api_new_token = get_credentials()[0]

    ''' formatting date '''
    global timeto, timetill
    timeto = timeto.strftime("%Y-%m-%dT%H:%M:%S")
    timetill = timetill.strftime("%Y-%m-%dT%H:%M:%S")

    
    ''' Identify the item '''
    resource_id = (
        "subscriptions/{}/"
        "resourceGroups/{}/"
        "providers/{}/{}"
    ).format(subscription_id, resource_group, resource_type_list[resource_type],  resource_name)

    api_url = "https://{}/{}/providers/microsoft.insights/metrics?api-version=2018-01-01&metricnames={}&timespan={}Z/{}Z".format(resource_id, az_metric, timeto, timetill)

    ''' Aggregations: Total, Sum, Count, Minimum, Maximum, Average'''
    ''' https://docs.microsoft.com/en-us/azure/azure-monitor/essentials/metrics-aggregation-explained '''

    ''' Adjustment on aggregation values '''
    t_range = (timetill - timeto).seconds
    #if ( resource_type == "ADF" ):
    if t_range > 3600:
        default_interval = "PT1H"
    else:
        default_interval = "PT1M"

    api_new_token = get_credentials()[0]
    headers = {}
    headers['Content-Type'] = "application/json" 
    headers['Authorization'] = "Bearer {}".format(api_new_token)
    headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36" 

    response = requests.post(api_url, headers=headers, timeout=10)

    # metrics_data = client.metrics.list(
    #     resource_id,
    #     timespan="{}/{}".format(timeto, timetill),
    #     interval=default_interval,
    #     metricnames=az_metric,
    #     aggregation=metric_aggregation.capitalize()
    # )

    # ''' Adjustment to print the right aggregation selected '''
    # aggregation_name= str("x." + metric_aggregation.lower())
    # metrics_data = metrics_data.value[0]

    # ''' Metrics involving API Management looks better using sum instead mean '''
    # if ( metric_aggregation.lower() == "minimum"):
    #     metrics_data = min(eval(aggregation_name) for x in metrics_data.timeseries[0].data)
    # elif ( metric_aggregation.lower() == "maximum" ):
    #     metrics_data = max(eval(aggregation_name) for x in metrics_data.timeseries[0].data)
    # elif ( metric_aggregation.lower() == "total" or metric_aggregation.lower() == "count" ):
    #         metrics_data = sum(eval(aggregation_name) for x in metrics_data.timeseries[0].data)
    # else:
    #     try:
    #         metrics_data = fmean(eval(aggregation_name) for x in metrics_data.timeseries[0].data)
    #     except:
    #         metrics_data = mean(eval(aggregation_name) for x in metrics_data.timeseries[0].data)
    # # except:
    # #     metrics_data = 0

    # client.close()
    return metrics_data

''' For menu '''
def main(credentials):
    ''' Limit timerange - default is 60 seconds'''
    if (options.az_timerange != None ):
        timerange = ''.join(str(e) for e in options.az_timerange)
        timerange = int(timerange)
        metrics_timerange(minutes=timerange)
    else:
        metrics_timerange()

    get_credentials(credentials=credentials)
    if (options.az_metric_list != None or options.az_metrics != None ):
        #AZ Metrics
        try:
            az_metrics_options = ''.join(str(e) for e in options.az_metric_list)
        except:
            az_metrics_options = ''.join(str(e) for e in options.az_metrics)

        az_metrics_options = az_metrics_options.split(',')
        if len(az_metrics_options) <3:
                print("USAGE: resource_name, resource_group, resource_type")
                sys.exit(1)
        else:
            resource_name = az_metrics_options[0]
            resource_group = az_metrics_options[1]
            resource_type = az_metrics_options[2]
        
        ''' When metric list ... '''
        if (options.az_metric_list != None):
            azmonitor_available_metrics(resource_name=resource_name, resource_group=resource_group, resource_type=resource_type)
        else:
            ''' When just getting a single value ... '''
            az_metric = az_metrics_options[3]
            az_metric_aggregation = az_metrics_options[4]
            result = get_az_metrics(resource_name=resource_name, resource_group=resource_group, resource_type=resource_type, az_metric=az_metric, metric_aggregation=az_metric_aggregation)
            print(result)

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