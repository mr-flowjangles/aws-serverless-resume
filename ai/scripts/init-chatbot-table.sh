#!/bin/bash
# Initialize ChatbotRAG table and AI dependencies (only if chatbot is enabled in config)

echo "Checking chatbot configuration..."

# Check if config file exists
if [ ! -f "/app/ai/config.yml" ]; then
    echo "⚠️  AI config file not found at /app/ai/config.yml"
    echo "   Skipping ChatbotRAG initialization"
    exit 0
fi

# Read config and check if chatbot is enabled using Python
CHATBOT_ENABLED=$(python3 << 'EOF'
import yaml
import sys

try:
    with open('/app/ai/config.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    enabled = config.get('chatbot', {}).get('enabled', False)
    print('true' if enabled else 'false')
except Exception as e:
    print('false', file=sys.stderr)
    sys.exit(1)
EOF
)

if [ "$CHATBOT_ENABLED" != "true" ]; then
    echo "ℹ️  Chatbot is disabled in config (chatbot.enabled: false)"
    echo "   Skipping ChatbotRAG initialization"
    exit 0
fi

echo "✓ Chatbot is enabled - initializing AI components..."
echo ""

# Install AI dependencies
echo "📦 Installing AI dependencies..."
if [ -f "/app/ai/requirements.txt" ]; then
    pip install -q -r /app/ai/requirements.txt
    if [ $? -eq 0 ]; then
        echo "  ✓ AI dependencies installed successfully"
    else
        echo "  ⚠️  Failed to install some dependencies (may already be installed)"
    fi
else
    echo "  ⚠️  AI requirements.txt not found, skipping dependency installation"
fi
echo ""

# Wait for LocalStack to be ready
echo "⏳ Waiting for LocalStack..."
sleep 2

# Create ChatbotRAG table
echo "📊 Creating ChatbotRAG table..."
aws --endpoint-url=http://localstack:4566 dynamodb create-table \
    --table-name ChatbotRAG \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
        AttributeName=type,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=TypeIndex,KeySchema=[{AttributeName=type,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
    --billing-mode PROVISIONED \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-1 2>/dev/null

if [ $? -eq 0 ]; then
    echo "  ✅ ChatbotRAG table created successfully!"
else
    echo "  ⚠️  ChatbotRAG table may already exist or creation failed"
fi

echo ""
echo "✅ ChatbotRAG initialization complete!"
echo ""