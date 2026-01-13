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
