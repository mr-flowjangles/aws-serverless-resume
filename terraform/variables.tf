variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "domain_name" {
  description = "Domain name for the resume site"
  type        = string
  default     = "robrose.info"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "aws-serverless-resume"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}
variable "recaptcha_secret_key" {
  description = "Google reCAPTCHA secret key for contact form"
  type        = string
  sensitive   = true
  default     = ""
}
variable "notification_email" {
  description = "Email address to receive contact form notifications"
  type        = string
  default     = ""
}