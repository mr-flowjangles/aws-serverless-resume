import boto3
import os
import time
import subprocess
import sys
from pathlib import Path

def seed_database():
    """Seed DynamoDB with initial data if table is empty"""
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    
    table = dynamodb.Table('ResumeData')
    
    # Wait for table to exist (retry up to 10 times)
    print("Waiting for DynamoDB table...")
    for i in range(10):
        try:
            response = table.scan(Limit=1)
            break
        except Exception as e:
            if i < 9:
                print(f"  Table not ready yet, retrying... ({i+1}/10)")
                time.sleep(2)
            else:
                print("  Table not available after 10 retries, skipping seed")
                return
    
    # Check if table has data
    if response['Count'] > 0:
        print("Database already seeded, skipping...")
        return
    
    # Load data from Excel template
    template_path = Path("/app/scripts/resume-data-template.xlsx")
    
    if not template_path.exists():
        print(f"⚠️  Template file not found at {template_path}")
        print("  Skipping database seed")
        return
    
    print(f"📊 Loading resume data from template...")
    
    # Run load_resume.py script
    try:
        result = subprocess.run(
            [sys.executable, "/app/scripts/load_resume.py", str(template_path)],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        print("✅ Database seeding complete")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error loading resume data:")
        print(e.stderr)
        print("  Database seed failed")
    except Exception as e:
        print(f"❌ Unexpected error during seed: {e}")
