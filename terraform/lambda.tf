# Archive the entire FastAPI application
data "archive_file" "fastapi_app" {
  type        = "zip"
  source_dir  = "${path.module}/../api"
  output_path = "${path.module}/builds/fastapi-app.zip"
  
  excludes = [
    "__pycache__",
    "*.pyc",
    ".pytest_cache",
    "tests",
    "Dockerfile",
  ]
}

# Single Lambda function running the entire FastAPI app
resource "aws_lambda_function" "fastapi_app" {
  filename         = data.archive_file.fastapi_app.output_path
  function_name    = "${var.project_name}-api"
  role             = aws_iam_role.lambda_execution.arn
  handler          = "lambda_handler.handler"
  source_code_hash = data.archive_file.fastapi_app.output_base64sha256
  runtime          = "python3.12"
  timeout          = 30
  memory_size      = 512

  environment {
    variables = {
      DYNAMODB_TABLE       = aws_dynamodb_table.resume_data.name
      RECAPTCHA_SECRET_KEY = var.recaptcha_secret_key
      AWS_REGION           = var.aws_region
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
