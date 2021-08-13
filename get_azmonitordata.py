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

resource_id = (
    "subscriptions/{}/"
    "resourceGroups/{}/"
    "providers/Microsoft.ContainerService/managedClusters/{}"
).format(subscription_id, resource_group_name, resource_name)


endtime = datetime.utcnow()
starttime = datetime.utcnow() - timedelta(minutes=2) 


metrics_data = client.metrics.list(
    resource_id,
    timespan="{}/{}".format(starttime, endtime),
    interval='PT1M',
    metricnames='kube_pod_status_ready',
    aggregation='Total'
)

for item in metrics_data.value:
   # azure.mgmt.monitor.models.Metric
   print("{} ({})".format(item.name.localized_value, item.unit.name))
   for timeserie in item.timeseries:
       for data in timeserie.data:
           # azure.mgmt.monitor.models.MetricData
           print("{}: {}".format(data.time_stamp, data.total))