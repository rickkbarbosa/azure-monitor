# azure-monitor
A proof-of-concept to get Azure monitor metrics by Python

# How to
You could have a Azure Service principal created and keep yout variables, for example:

```
az ad sp create-for-rbac --name azure-monitor-test
```

And result will be something like:

```
{
  "appId": "aaaaaa-1234-5c67-0000-abcdefg",
  "displayName": "azure-monitor-test",
  "name": "http://azure-monitor-test",
  "password": "s3cret",
  "tenant": "123az567-89ad-99aa-bbcc1-abvcdfa"
```


Or declare using environment variables:

```
export AZ_TENANT_ID="something"
export AZ_APP_ID="something"
export AZ_APP_PASSWORD="something"
export AZ_SUBSCRIPTION_ID="something"
```

#List AZ Resource Groups
#az group list --output table


# USAGE:

To discover Available Metrics for a Azure product:
```
get_azmonitordata.py -M "name,resource_group_name,type"
```

To get AZ Metric values:
```
get_azmonitordata.py -m "name,resource_group_name,type,metric_name,aggregation"
``` 

_type_: Azure Components granted by this script. :

* AKS: Azure Kubernetes Services
* ADF: Data Factory
* APIM: API Management
* VM: Virtual Machines


_aggregation_ : metric aggregation, depends of metric

* total: Gets all values in a timerange, and sums it.
* average: presents a mean value in the timerange.



TODO:

* Aggregate others Azure components [in the list](https://docs.microsoft.com/pt-br/azure/azure-monitor/essentials/metrics-supported)
* Improve the aggregations calc (mean, fmean, sum...)
* AKS: Split metrics by nodes (e.g: node memory, presenting each node separated)
* Include an option in order to input custom  timeranges