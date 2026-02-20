# Lambda deployment package (built using Docker via build-lambda.sh script)
# The package includes all Python dependencies compiled for Lambda's runtime

# Single Lambda function running the entire FastAPI app
resource "aws_lambda_function" "fastapi_app" {
  s3_bucket        = "aws-serverless-resume-prod"
  s3_key           = "lambda/fastapi-app.zip"
  function_name    = "${var.project_name}-api"
  role             = aws_iam_role.lambda_execution.arn
  handler          = "run.sh"
  source_code_hash = filebase64sha256("${path.module}/builds/fastapi-app.zip")
  runtime          = "python3.12"
  timeout          = 30
  memory_size      = 512

  layers = [
    "arn:aws:lambda:us-east-1:753240598075:layer:LambdaAdapterLayerX86:24"
  ]

  environment {
    variables = {
      DYNAMODB_TABLE          = aws_dynamodb_table.resume_data.name
      RECAPTCHA_SECRET_KEY    = var.recaptcha_secret_key
      SES_FROM_EMAIL          = "robmrose@me.com"
      SES_TO_EMAIL            = "robmrose@me.com"
      OPENAI_API_KEY          = var.openai_api_key
      ANTHROPIC_API_KEY       = var.anthropic_api_key
      AWS_LWA_PORT            = "8080"
      AWS_LAMBDA_EXEC_WRAPPER = "/opt/bootstrap"
      AWS_LWA_INVOKE_MODE = "response_stream"
    }
  }

  tags = {
    Name        = "${var.project_name}-api"
    Environment = var.environment
  }
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fastapi_app.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.resume_api.execution_arn}/*/*"
}

# Lambda Function URL for streaming (bypasses API Gateway)
resource "aws_lambda_function_url" "streaming" {
  function_name      = aws_lambda_function.fastapi_app.function_name
  authorization_type = "NONE"
  invoke_mode = "RESPONSE_STREAM"
}

output "streaming_url" {
  value = aws_lambda_function_url.streaming.function_url
}

resource "aws_lambda_permission" "function_url_public" {
  statement_id           = "FunctionURLAllowPublicAccess"
  action                 = "lambda:InvokeFunctionUrl"
  function_name          = aws_lambda_function.fastapi_app.function_name
  principal              = "*"
  function_url_auth_type = "NONE"
}