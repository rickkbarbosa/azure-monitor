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