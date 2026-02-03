# DynamoDB table for resume data
resource "aws_dynamodb_table" "resume_data" {
  name         = "ResumeData"
  billing_mode = "PAY_PER_REQUEST" # On-demand pricing
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "type"
    type = "S"
  }

  # Global Secondary Index for querying by type
  global_secondary_index {
    name            = "TypeIndex"
    hash_key        = "type"
    projection_type = "ALL"
  }

  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name        = "${var.project_name}-dynamodb"
    Environment = var.environment
    Project     = var.project_name
  }
}

# DynamoDB table for chatbot RAG embeddings
resource "aws_dynamodb_table" "chatbot_rag" {
  name         = "ChatbotRAG"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name        = "${var.project_name}-chatbot-rag"
    Environment = var.environment
    Project     = var.project_name
  }
}

# DynamoDB table for chatbot logs
resource "aws_dynamodb_table" "chatbot_logs" {
  name         = "ChatbotLogs"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name        = "${var.project_name}-chatbot-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}