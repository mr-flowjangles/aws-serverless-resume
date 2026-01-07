import boto3
import os
import json
import time
from pathlib import Path

def load_seed_data():
    """Load seed data from config file"""
    seed_path = Path("/app/config/seed-data.json")
    try:
        with open(seed_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Seed data file not found")
        return None
    except json.JSONDecodeError:
        print("Invalid seed data file")
        return None

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
    
    # Load and insert seed data
    seed_data = load_seed_data()
    if not seed_data:
        return
    
    print("Seeding database...")
    
    # Insert experience items
    for exp in seed_data.get('experience', []):
        table.put_item(Item=exp)
        print(f"  Added: {exp['company']} - {exp['title']}")
    
    print("Database seeding complete")