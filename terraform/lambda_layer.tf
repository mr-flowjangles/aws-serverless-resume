# Lambda Layer for shared code
# This contains the shared/handlers code that all Lambda functions use

# Archive the shared code
data "archive_file" "shared_layer" {
  type        = "zip"
  source_dir  = "${path.module}/../api/shared"
  output_path = "${path.module}/builds/shared-layer.zip"
}

# Create Lambda Layer
resource "aws_lambda_layer_version" "shared" {
  filename            = data.archive_file.shared_layer.output_path
  layer_name          = "${var.project_name}-shared-layer"
  source_code_hash    = data.archive_file.shared_layer.output_base64sha256
  compatible_runtimes = ["python3.12"]

  description = "Shared business logic for resume API"
}
