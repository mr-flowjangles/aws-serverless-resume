#!/bin/bash

echo "Waiting for LocalStack to be ready..."
sleep 5

echo "Creating DynamoDB table..."
aws --endpoint-url=http://localstack:4566 dynamodb create-table \
    --table-name ResumeData \
    --attribute-definitions AttributeName=id,AttributeType=S AttributeName=type,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=TypeIndex,KeySchema=[{AttributeName=type,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
    --billing-mode PROVISIONED \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-1 2>/dev/null

if [ $? -eq 0 ]; then
    echo "Table created successfully"
else
    echo "Table may already exist or creation failed"
fi

echo "Creating ChatbotRAG table..."
aws --endpoint-url=http://localstack:4566 dynamodb create-table \
    --table-name ChatbotRAG \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --billing-mode PROVISIONED \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-1 2>/dev/null

if [ $? -eq 0 ]; then
    echo "ChatbotRAG table created successfully"
else
    echo "ChatbotRAG table may already exist or creation failed"
fi

echo "Creating ChatbotLogs table..."
aws --endpoint-url=http://localstack:4566 dynamodb create-table \
    --table-name ChatbotLogs \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1 2>/dev/null

if [ $? -eq 0 ]; then
    echo "ChatbotLogs table created successfully"
else
    echo "ChatbotLogs table may already exist or creation failed"
fi