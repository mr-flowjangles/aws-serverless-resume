#!/bin/bash
set -e

# Build Lambda deployment package using Docker
# This ensures dependencies are compiled for the Lambda runtime environment

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
API_DIR="$PROJECT_ROOT/api"
TERRAFORM_DIR="$PROJECT_ROOT/terraform"
BUILD_DIR="$TERRAFORM_DIR/builds"
OUTPUT_ZIP="$BUILD_DIR/fastapi-app.zip"

echo "🏗️  Building Lambda deployment package..."

# Create builds directory if it doesn't exist
mkdir -p "$BUILD_DIR"

# Remove old build if exists
rm -f "$OUTPUT_ZIP"

# Build the container with dependencies
echo "📦 Installing dependencies in Lambda-compatible environment..."
cd "$API_DIR"
docker build --platform linux/amd64 -f Dockerfile.lambda -t lambda-builder:latest .

# Create a temporary container and extract the /asset directory
echo "📤 Extracting build artifacts..."
CONTAINER_ID=$(docker create lambda-builder:latest)
cd "$BUILD_DIR"
docker cp "$CONTAINER_ID:/asset" ./lambda-package
docker rm "$CONTAINER_ID"

# Create the zip file
echo "🗜️  Creating deployment package..."
cd lambda-package
zip -r "$OUTPUT_ZIP" . -x "*.git*" > /dev/null
cd ..
rm -rf lambda-package

echo "✅ Lambda package created: $OUTPUT_ZIP"
echo "📊 Package size: $(du -h "$OUTPUT_ZIP" | cut -f1)"
