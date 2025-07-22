#!/bin/bash

# Azure Deployment Script for RFX Assessment Streamlit App
# Make sure you have Azure CLI installed and are logged in

# Configuration variables
RESOURCE_GROUP="rg-rfx-assessment"
LOCATION="eastus"
ACR_NAME="acrfxassessment"
APP_NAME="rfx-assessment-app"
CONTAINER_APP_ENV="rfx-assessment-env"
IMAGE_NAME="rfx-assessment"
TAG="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Azure deployment for RFX Assessment App${NC}"

# Step 1: Create Resource Group
echo -e "${YELLOW}📦 Creating resource group...${NC}"
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION

# Step 2: Create Azure Container Registry
echo -e "${YELLOW}🏗️ Creating Azure Container Registry...${NC}"
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true

# Step 3: Login to ACR
echo -e "${YELLOW}🔐 Logging into Azure Container Registry...${NC}"
az acr login --name $ACR_NAME

# Step 4: Build and push Docker image
echo -e "${YELLOW}🔨 Building Docker image...${NC}"
docker build -t $IMAGE_NAME:$TAG .

echo -e "${YELLOW}🏷️ Tagging image for ACR...${NC}"
docker tag $IMAGE_NAME:$TAG $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG

echo -e "${YELLOW}📤 Pushing image to ACR...${NC}"
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG

# Step 5: Create Container Apps Environment
echo -e "${YELLOW}🌍 Creating Container Apps environment...${NC}"
az containerapp env create \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Step 6: Get ACR credentials
echo -e "${YELLOW}🔑 Getting ACR credentials...${NC}"
ACR_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query passwords[0].value --output tsv)

# Step 7: Create Container App
echo -e "${YELLOW}🚢 Creating Container App...${NC}"
az containerapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENV \
    --image $ACR_SERVER/$IMAGE_NAME:$TAG \
    --registry-server $ACR_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --target-port 8080 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 5 \
    --cpu 1.0 \
    --memory 2.0Gi \
    --env-vars \
        AZURE_AI_PROJECT_ENDPOINT="<your-ai-foundry-endpoint>" \
        AZURE_SUBSCRIPTION_ID="<your-subscription-id>" \
        AZURE_RESOURCE_GROUP="<your-ai-foundry-rg>"

# Step 8: Get app URL
echo -e "${YELLOW}🔗 Getting application URL...${NC}"
APP_URL=$(az containerapp show \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    --output tsv)

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}🌐 Your app is available at: https://$APP_URL${NC}"

# Optional: Set up monitoring
echo -e "${YELLOW}📊 Setting up monitoring (optional)...${NC}"
az monitor log-analytics workspace create \
    --resource-group $RESOURCE_GROUP \
    --workspace-name "rfx-assessment-logs" \
    --location $LOCATION

echo -e "${GREEN}🎉 Deployment script completed!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Update environment variables in the Container App with your actual Azure AI Foundry credentials"
echo -e "2. Configure custom domain (if needed)"
echo -e "3. Set up SSL certificate (if using custom domain)"
echo -e "4. Configure authentication (if required)"

# Cleanup function (uncomment to run)
# cleanup() {
#     echo -e "${RED}🧹 Cleaning up resources...${NC}"
#     az group delete --name $RESOURCE_GROUP --yes --no-wait
#     echo -e "${GREEN}✅ Cleanup initiated${NC}"