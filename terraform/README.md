# Terraform Infrastructure for AWS Serverless Resume

This Terraform configuration deploys the frontend infrastructure for the serverless resume website.

## Architecture

- **S3**: Private bucket for static website content
- **CloudFront**: CDN with Origin Access Control (OAC) for secure S3 access
- **Route 53**: DNS records pointing to CloudFront
- **ACM**: SSL/TLS certificate for HTTPS

## Prerequisites

1. AWS CLI configured with appropriate credentials
2. Terraform >= 1.0 installed
3. Domain `robrose.info` already registered in Route 53

## Deployment Steps

### 1. Initialize Terraform

```bash
cd terraform
terraform init
```

### 2. Review the Plan

```bash
terraform plan
```

### 3. Apply the Configuration

```bash
terraform apply
```

This will:
- Create S3 bucket with versioning enabled
- Request ACM certificate and validate via DNS
- Create CloudFront distribution with HTTPS
- Update Route 53 DNS records

**Note:** Certificate validation can take 5-30 minutes.

### 4. Upload Website Content

After infrastructure is deployed, upload your static files:

```bash
aws s3 sync ../app/ s3://aws-serverless-resume-prod/ --delete
```

### 5. Invalidate CloudFront Cache

After uploading new content:

```bash
aws cloudfront create-invalidation \
  --distribution-id $(terraform output -raw cloudfront_distribution_id) \
  --paths "/*"
```

## Outputs

After deployment, Terraform will output:
- `website_url`: Your website URL (https://robrose.info)
- `s3_bucket_name`: S3 bucket name for uploads
- `cloudfront_distribution_id`: CloudFront distribution ID for cache invalidation

## Cost Estimation

- **S3**: ~$0.023/GB storage + $0.09/GB transfer
- **CloudFront**: First 1TB/month is $0.085/GB
- **Route 53**: $0.50/hosted zone/month
- **ACM Certificate**: FREE

**Estimated monthly cost for low-traffic site: $1-5/month**

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning:** This will delete your S3 bucket and all content!
