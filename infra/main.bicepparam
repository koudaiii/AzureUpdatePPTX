using 'main.bicep'

param suffixName = 'pr-123'
param location = 'Australia East'
param apiKey = readEnvironmentVariable('API_KEY', 'defaultApiKey')
param apiEndpoint = readEnvironmentVariable('API_ENDPOINT', 'https://api.example.com')
param dockerImage = 'koudaiii/azureupdatepptx:latest'
param tags = {
  project: 'AzureUpdatePPTX'
  managed_by: 'bicep'
  pr_number: '123'
}
