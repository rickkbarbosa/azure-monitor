#!/bin/env python
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


parser = argparse.ArgumentParser()
parser.add_argument("-C", "--credentials", dest="az_credentials", nargs=1, help="Declare AZ credentials [tenant_id,app_id,app_password,subscription_id]")
parser.add_argument("-M", "--metric-list", dest="az_metric_list", nargs=1, help="List available metrics for a resource")
parser.add_argument("-m", "--metric", dest="az_metrics", nargs=1, help="Get metrics for a resource")
parser.allow_interspersed_args = False
(options, args) = parser.parse_known_args()

''' Setting the right resource type '''
resource_type_list = {}
resource_type_list['AKS'] = "Microsoft.ContainerService/managedClusters"
resource_type_list['APIM'] =  "Microsoft.ApiManagement/service"
resource_type_list['VM'] = "Microsoft.Compute/virtualMachines"


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
    global client
    client = MonitorManagementClient(
        credentials,
        subscription_id
    )

    return client, subscription_id


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
    ''' Identify the item '''
    resource_id = (
        "subscriptions/{}/"
        "resourceGroups/{}/"
        "providers/{}/{}"
    ).format(subscription_id, resource_group, resource_type_list[resource_type],  resource_name)

    ''' Aggregations: Total, Sum, Count, Minimum, Maximum, Average'''
    ''' https://docs.microsoft.com/en-us/azure/azure-monitor/essentials/metrics-aggregation-explained '''
    metrics_data = client.metrics.list(
        resource_id,
        timespan="{}/{}".format(timeto, timetill),
        interval='PT1M',
        metricnames=az_metric,
        aggregation=metric_aggregation.capitalize()
    )

    # for item in metrics_data.value:
    #    print("{} ({})".format(item.name.localized_value, item.unit.name))
    #    for timeserie in item.timeseries:
    #        for data in timeserie.data:
    #            print("{}: {}".format(data.time_stamp, data.total))

    #metrics_data.value[0].timeseries[0].data[1].total

    ''' Adjustment to print the right aggregation selected '''
    aggregation_name= str("x." + metric_aggregation.lower())
    metrics_data = metrics_data.value[0]

    ''' Metrics involving API Management looks better using sum instead mean '''
    if ( resource_type == "APIM" ):
        metrics_data = sum(eval(aggregation_name) for x in metrics_data.timeseries[0].data)
    else:
        try:
            metrics_data = fmean(eval(aggregation_name) for x in metrics_data.timeseries[0].data)
        except:
            metrics_data = mean(eval(aggregation_name) for x in metrics_data.timeseries[0].data)

    return metrics_data

''' For menu '''
def main(credentials):
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