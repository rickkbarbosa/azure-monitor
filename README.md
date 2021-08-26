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
* WEB: App WebServices
* SQL: Azure databases
* CONNECTION: Azur connections


_aggregation_ : metric aggregation, depends of metric

* total: Gets all values in a timerange, and sums it.
* average: presents a mean value in the timerange.

SPECIFIC TIMERANGES (default is 5)

Use the  option _-t_ to define a custom time minute range, in minutes. Example:

```
./az_getmonitormetrics.py -m "cclient-aks-prod,resourcegroup_name,AKS,node_disk_usage_bytes,average" -t 10
```


TODO:

* Aggregate others Azure components [in the list](https://docs.microsoft.com/pt-br/azure/azure-monitor/essentials/metrics-supported)
* AKS: Split metrics by nodes (e.g: node memory, presenting each node separated)




### BUY ME A COFFEE ;) 


* [Paypal](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=29JLND674CAGY&currency_code=BRL)
