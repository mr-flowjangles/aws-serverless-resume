# API Gateway REST API
resource "aws_api_gateway_rest_api" "resume_api" {
  name        = "${var.project_name}-api"
  description = "Resume API Gateway"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Name        = "${var.project_name}-api"
    Environment = var.environment
  }
}

# /resume resource
resource "aws_api_gateway_resource" "resume" {
  rest_api_id = aws_api_gateway_rest_api.resume_api.id
  parent_id   = aws_api_gateway_rest_api.resume_api.root_resource_id
  path_part   = "resume"
}

# /resume/profile resource
resource "aws_api_gateway_resource" "profile" {
  rest_api_id = aws_api_gateway_rest_api.resume_api.id
  parent_id   = aws_api_gateway_resource.resume.id
  path_part   = "profile"
}

resource "aws_api_gateway_method" "profile_get" {
  rest_api_id   = aws_api_gateway_rest_api.resume_api.id
  resource_id   = aws_api_gateway_resource.profile.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "profile" {
  rest_api_id             = aws_api_gateway_rest_api.resume_api.id
  resource_id             = aws_api_gateway_resource.profile.id
  http_method             = aws_api_gateway_method.profile_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.profile.invoke_arn
}

# /resume/work-experience resource
resource "aws_api_gateway_resource" "work_experience" {
  rest_api_id = aws_api_gateway_rest_api.resume_api.id
  parent_id   = aws_api_gateway_resource.resume.id
  path_part   = "work-experience"
}

resource "aws_api_gateway_method" "work_experience_get" {
  rest_api_id   = aws_api_gateway_rest_api.resume_api.id
  resource_id   = aws_api_gateway_resource.work_experience.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "work_experience" {
  rest_api_id             = aws_api_gateway_rest_api.resume_api.id
  resource_id             = aws_api_gateway_resource.work_experience.id
  http_method             = aws_api_gateway_method.work_experience_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.work_experience.invoke_arn
}

# /resume/education resource
resource "aws_api_gateway_resource" "education" {
  rest_api_id = aws_api_gateway_rest_api.resume_api.id
  parent_id   = aws_api_gateway_resource.resume.id
  path_part   = "education"
}

resource "aws_api_gateway_method" "education_get" {
  rest_api_id   = aws_api_gateway_rest_api.resume_api.id
  resource_id   = aws_api_gateway_resource.education.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "education" {
  rest_api_id             = aws_api_gateway_rest_api.resume_api.id
  resource_id             = aws_api_gateway_resource.education.id
  http_method             = aws_api_gateway_method.education_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.education.invoke_arn
}

# /resume/skills resource
resource "aws_api_gateway_resource" "skills" {
  rest_api_id = aws_api_gateway_rest_api.resume_api.id
  parent_id   = aws_api_gateway_resource.resume.id
  path_part   = "skills"
}

resource "aws_api_gateway_method" "skills_get" {
  rest_api_id   = aws_api_gateway_rest_api.resume_api.id
  resource_id   = aws_api_gateway_resource.skills.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "skills" {
  rest_api_id             = aws_api_gateway_rest_api.resume_api.id
  resource_id             = aws_api_gateway_resource.skills.id
  http_method             = aws_api_gateway_method.skills_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.skills.invoke_arn
}

# /contact resource
resource "aws_api_gateway_resource" "contact" {
  rest_api_id = aws_api_gateway_rest_api.resume_api.id
  parent_id   = aws_api_gateway_rest_api.resume_api.root_resource_id
  path_part   = "contact"
}

resource "aws_api_gateway_method" "contact_post" {
  rest_api_id   = aws_api_gateway_rest_api.resume_api.id
  resource_id   = aws_api_gateway_resource.contact.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "contact" {
  rest_api_id             = aws_api_gateway_rest_api.resume_api.id
  resource_id             = aws_api_gateway_resource.contact.id
  http_method             = aws_api_gateway_method.contact_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.contact.invoke_arn
}

# /health resource
resource "aws_api_gateway_resource" "health" {
  rest_api_id = aws_api_gateway_rest_api.resume_api.id
  parent_id   = aws_api_gateway_rest_api.resume_api.root_resource_id
  path_part   = "health"
}

resource "aws_api_gateway_method" "health_get" {
  rest_api_id   = aws_api_gateway_rest_api.resume_api.id
  resource_id   = aws_api_gateway_resource.health.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "health" {
  rest_api_id             = aws_api_gateway_rest_api.resume_api.id
  resource_id             = aws_api_gateway_resource.health.id
  http_method             = aws_api_gateway_method.health_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.health.invoke_arn
}

# CORS configuration for all methods
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
      aws_api_gateway_resource.profile.id,
      aws_api_gateway_method.profile_get.id,
      aws_api_gateway_integration.profile.id,
      aws_api_gateway_resource.work_experience.id,
      aws_api_gateway_method.work_experience_get.id,
      aws_api_gateway_integration.work_experience.id,
      aws_api_gateway_resource.education.id,
      aws_api_gateway_method.education_get.id,
      aws_api_gateway_integration.education.id,
      aws_api_gateway_resource.skills.id,
      aws_api_gateway_method.skills_get.id,
      aws_api_gateway_integration.skills.id,
      aws_api_gateway_resource.contact.id,
      aws_api_gateway_method.contact_post.id,
      aws_api_gateway_integration.contact.id,
      aws_api_gateway_resource.health.id,
      aws_api_gateway_method.health_get.id,
      aws_api_gateway_integration.health.id,
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
