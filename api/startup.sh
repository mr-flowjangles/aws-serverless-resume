#!/bin/bash
# API Container Startup Script
# Checks if chatbot is enabled and installs AI dependencies if needed

echo "🚀 Starting API container..."

# Check if chatbot is enabled
if [ -f "/app/ai/config.yml" ]; then
    CHATBOT_ENABLED=$(python3 << 'EOF'
import yaml
try:
    with open('/app/ai/config.yml', 'r') as f:
        config = yaml.safe_load(f)
    enabled = config.get('chatbot', {}).get('enabled', False)
    print('true' if enabled else 'false')
except:
    print('false')
EOF
)

    if [ "$CHATBOT_ENABLED" = "true" ]; then
        echo "✓ Chatbot enabled - checking AI dependencies..."
        
        # Check if openai is already installed
        python3 -c "import openai" 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "📦 Installing AI dependencies..."
            pip install -q -r /app/ai/requirements.txt
            echo "  ✓ AI dependencies installed"
        else
            echo "  ✓ AI dependencies already installed"
        fi
    fi
fi

# Start the API server
echo "🌐 Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
