#!/bin/env python
#https://docs.microsoft.com/pt-br/python/api/overview/azure/monitoring?view=azure-python
#https://docs.microsoft.com/en-us/azure/azure-monitor/essentials/metrics-supported#microsoftkubernetesconnectedclusters
import os
from datetime import timedelta
from datetime import datetime
from azure.mgmt.monitor import MonitorManagementClient
from azure.common.credentials import ServicePrincipalCredentials

az_tenant_id = os.environ['AZ_TENANT_ID']
az_app_id = os.environ['AZ_APP_ID']
az_password = os.environ['AZ_APP_PASSWORD']

subscription_id = os.environ['AZ_SUBSCRIPTION_ID']

resource_group_name = os.environ['AZ_RESOURCE_GROUP']
resource_name = os.environ['AZ_RESOURCE_NAME']

resource_type = os.environ['AZ_RESOURCE_TYPE']

''' Starting credential login '''
credentials = ServicePrincipalCredentials(
    client_id = az_app_id,
    secret = az_password,
    tenant = az_tenant_id
)

#Conection itself
client = MonitorManagementClient(
    credentials,
    subscription_id
)

''' Setting the right resource type '''
resource_type_list = {}
resource_type_list['AKS'] = "Microsoft.ContainerService/managedClusters"
resource_type_list['VM'] = "Microsoft.Compute/virtualMachines"

''' Identify the item '''
resource_id = (
    "subscriptions/{}/"
    "resourceGroups/{}/"
    "providers/{}/{}"
).format(subscription_id, resource_group_name, resource_type_list[resource_type],  resource_name)


endtime = datetime.utcnow()
starttime = datetime.utcnow() - timedelta(minutes=2) 

def azmonitor_available_metrics():
    for metric in client.metric_definitions.list(resource_id):
        # azure.monitor.models.MetricDefinition
        print("{}: id={}, unit={}".format(
            metric.name.localized_value,
            metric.name.value,
            metric.unit
        ))

metrics_data = client.metrics.list(
    resource_id,
    timespan="{}/{}".format(starttime, endtime),
    interval='PT1M',
    metricnames='kube_pod_status_ready',
    aggregation='Total'
)

for item in metrics_data.value:
   print("{} ({})".format(item.name.localized_value, item.unit.name))
   for timeserie in item.timeseries:
       for data in timeserie.data:
           print("{}: {}".format(data.time_stamp, data.total))