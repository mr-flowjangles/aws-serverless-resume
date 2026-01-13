# Archive Lambda function code
data "archive_file" "lambda_profile" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda/profile"
  output_path = "${path.module}/builds/profile.zip"
}

data "archive_file" "lambda_work_experience" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda/work_experience"
  output_path = "${path.module}/builds/work_experience.zip"
}

data "archive_file" "lambda_education" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda/education"
  output_path = "${path.module}/builds/education.zip"
}

data "archive_file" "lambda_skills" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda/skills"
  output_path = "${path.module}/builds/skills.zip"
}

data "archive_file" "lambda_contact" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda/contact"
  output_path = "${path.module}/builds/contact.zip"
}

data "archive_file" "lambda_health" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda/health"
  output_path = "${path.module}/builds/health.zip"
}

# Lambda Functions
resource "aws_lambda_function" "profile" {
  filename         = data.archive_file.lambda_profile.output_path
  function_name    = "${var.project_name}-profile"
  role             = aws_iam_role.lambda_execution.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_profile.output_base64sha256
  runtime          = "python3.12"
  timeout          = 30

  layers = [aws_lambda_layer_version.shared.arn]

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.resume_data.name
    }
  }

  tags = {
    Name        = "${var.project_name}-profile"
    Environment = var.environment
  }
}

resource "aws_lambda_function" "work_experience" {
  filename         = data.archive_file.lambda_work_experience.output_path
  function_name    = "${var.project_name}-work-experience"
  role             = aws_iam_role.lambda_execution.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_work_experience.output_base64sha256
  runtime          = "python3.12"
  timeout          = 30

  layers = [aws_lambda_layer_version.shared.arn]

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.resume_data.name
    }
  }

  tags = {
    Name        = "${var.project_name}-work-experience"
    Environment = var.environment
  }
}

resource "aws_lambda_function" "education" {
  filename         = data.archive_file.lambda_education.output_path
  function_name    = "${var.project_name}-education"
  role             = aws_iam_role.lambda_execution.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_education.output_base64sha256
  runtime          = "python3.12"
  timeout          = 30

  layers = [aws_lambda_layer_version.shared.arn]

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.resume_data.name
    }
  }

  tags = {
    Name        = "${var.project_name}-education"
    Environment = var.environment
  }
}

resource "aws_lambda_function" "skills" {
  filename         = data.archive_file.lambda_skills.output_path
  function_name    = "${var.project_name}-skills"
  role             = aws_iam_role.lambda_execution.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_skills.output_base64sha256
  runtime          = "python3.12"
  timeout          = 30

  layers = [aws_lambda_layer_version.shared.arn]

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.resume_data.name
    }
  }

  tags = {
    Name        = "${var.project_name}-skills"
    Environment = var.environment
  }
}

resource "aws_lambda_function" "contact" {
  filename         = data.archive_file.lambda_contact.output_path
  function_name    = "${var.project_name}-contact"
  role             = aws_iam_role.lambda_execution.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_contact.output_base64sha256
  runtime          = "python3.12"
  timeout          = 30

  layers = [aws_lambda_layer_version.shared.arn]

  environment {
    variables = {
      DYNAMODB_TABLE       = aws_dynamodb_table.resume_data.name
      RECAPTCHA_SECRET_KEY = var.recaptcha_secret_key
    }
  }

  tags = {
    Name        = "${var.project_name}-contact"
    Environment = var.environment
  }
}

resource "aws_lambda_function" "health" {
  filename         = data.archive_file.lambda_health.output_path
  function_name    = "${var.project_name}-health"
  role             = aws_iam_role.lambda_execution.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_health.output_base64sha256
  runtime          = "python3.12"
  timeout          = 30

  layers = [aws_lambda_layer_version.shared.arn]

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.resume_data.name
    }
  }

  tags = {
    Name        = "${var.project_name}-health"
    Environment = var.environment
  }
}

# Lambda permissions for API Gateway
resource "aws_lambda_permission" "api_gateway_profile" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.profile.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.resume_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_work_experience" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.work_experience.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.resume_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_education" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.education.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.resume_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_skills" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.skills.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.resume_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_contact" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.contact.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.resume_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_health" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.health.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.resume_api.execution_arn}/*/*"
}
