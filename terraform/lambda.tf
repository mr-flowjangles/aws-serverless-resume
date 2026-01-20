# Lambda deployment package (built using Docker via build-lambda.sh script)
# The package includes all Python dependencies compiled for Lambda's runtime

# Single Lambda function running the entire FastAPI app
resource "aws_lambda_function" "fastapi_app" {
  filename         = "${path.module}/builds/fastapi-app.zip"
  function_name    = "${var.project_name}-api"
  role             = aws_iam_role.lambda_execution.arn
  handler          = "lambda_handler.handler"
  source_code_hash = filebase64sha256("${path.module}/builds/fastapi-app.zip")
  runtime          = "python3.12"
  timeout          = 30
  memory_size      = 512

  environment {
    variables = {
      DYNAMODB_TABLE       = aws_dynamodb_table.resume_data.name
      RECAPTCHA_SECRET_KEY = var.recaptcha_secret_key
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
