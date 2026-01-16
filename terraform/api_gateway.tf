# API Gateway REST API
resource "aws_api_gateway_rest_api" "resume_api" {
  name        = "${var.project_name}-api"
  description = "Resume API Gateway - proxies all requests to FastAPI Lambda"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Name        = "${var.project_name}-api"
    Environment = var.environment
  }
}

# Proxy resource to catch all paths
resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.resume_api.id
  parent_id   = aws_api_gateway_rest_api.resume_api.root_resource_id
  path_part   = "{proxy+}"
}

# ANY method for proxy (handles all HTTP methods)
resource "aws_api_gateway_method" "proxy_any" {
  rest_api_id   = aws_api_gateway_rest_api.resume_api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

# Integration: proxy everything to FastAPI Lambda
resource "aws_api_gateway_integration" "proxy" {
  rest_api_id             = aws_api_gateway_rest_api.resume_api.id
  resource_id             = aws_api_gateway_resource.proxy.id
  http_method             = aws_api_gateway_method.proxy_any.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.fastapi_app.invoke_arn
}

# Root path method (for /)
resource "aws_api_gateway_method" "root_any" {
  rest_api_id   = aws_api_gateway_rest_api.resume_api.id
  resource_id   = aws_api_gateway_rest_api.resume_api.root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
}

# Root integration
resource "aws_api_gateway_integration" "root" {
  rest_api_id             = aws_api_gateway_rest_api.resume_api.id
  resource_id             = aws_api_gateway_rest_api.resume_api.root_resource_id
  http_method             = aws_api_gateway_method.root_any.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.fastapi_app.invoke_arn
}

# CORS configuration
module "cors" {
  source  = "squidfunk/api-gateway-enable-cors/aws"
  version = "0.3.3"

  api_id          = aws_api_gateway_rest_api.resume_api.id
  api_resource_id = aws_api_gateway_rest_api.resume_api.root_resource_id
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "resume_api" {
  rest_api_id = aws_api_gateway_rest_api.resume_api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.proxy.id,
      aws_api_gateway_method.proxy_any.id,
      aws_api_gateway_integration.proxy.id,
      aws_api_gateway_method.root_any.id,
      aws_api_gateway_integration.root.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

# API Gateway Stage
resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.resume_api.id
  rest_api_id   = aws_api_gateway_rest_api.resume_api.id
  stage_name    = "prod"

  tags = {
    Name        = "${var.project_name}-api-prod"
    Environment = var.environment
  }
}
