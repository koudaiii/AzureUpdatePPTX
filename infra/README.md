# Infrastructure

This directory contains Bicep configuration for deploying AzureUpdatePPTX infrastructure using Azure Verified Modules (AVM).

## Architecture

- **App Service**: Linux-based container deployment using `avm/res/web/site`
- **App Service Plan**: Using `avm/res/web/serverfarm`
- **Resource Group**: PR-specific naming for easy cleanup

## Azure Verified Modules Used

- `avm/res/web/serverfarm` v0.3.0 - App Service Plan
- `avm/res/web/site` v0.11.0 - App Service deployment

## Usage

### Local Development

1. Edit `main.bicepparam` with your values

2. Deploy:
```bash
az deployment sub create \
  --location "Australia East" \
  --template-file main.bicep \
  --parameters @main.bicepparam
```

### GitHub Actions

manual deploy

## Required Secrets

Configure these in GitHub repository settings:

- `AZURE_CLIENT_ID`: Service Principal client ID
- `AZURE_TENANT_ID`: Azure tenant ID  
- `AZURE_SUBSCRIPTION_ID`: Azure subscription ID
- `API_KEY`: Azure OpenAI API Key
- `API_ENDPOINT`: Azure OpenAI API Endpoint

## Local

```console
$ az login

$ az deployment sub create \
          --location "Australia East" \
          --template-file infra/main.bicep \
          --parameters infra/main.bicepparam \
          --parameters suffixName="yyyymmdd" \
          --parameters dockerImage="koudaiii/azureupdatepptx:latest" \
          --parameters apiKey="<your-azure-openai-api-key>" \
          --parameters apiEndpoint="<your-azure-openai-api-endpoint>" \
          --parameters tags='{"project":"AzureUpdatePPTX","managed_by":"bicep","suffixName":"yyyymmdd"}' \
          --query 'properties.outputs.appServiceUrl.value' \
          --output tsv
https://app-azureupdatepptx-yyyymmdd.azurewebsites.net
```
