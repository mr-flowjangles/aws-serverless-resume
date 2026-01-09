#!/usr/bin/env python3
"""
Resume Data Loader
Reads resume data from Excel template and loads into DynamoDB
"""
import sys
import boto3
import pandas as pd
from pathlib import Path
import os

def load_work_experience(df):
    """Transform work experience data from DataFrame to DynamoDB format"""
    items = []
    
    for idx, row in df.iterrows():
        # Skip empty rows
        if pd.isna(row['job_title']) or pd.isna(row['company_name']):
            continue
            
        # Parse accomplishments (pipe-separated)
        accomplishments = []
        if pd.notna(row['accomplishments']):
            accomplishments = [a.strip() for a in str(row['accomplishments']).split('|')]
        
        # Handle is_current
        is_current = False
        if pd.notna(row['is_current']):
            is_current = str(row['is_current']).strip().upper() == 'TRUE'
        
        # Handle end_date
        end_date = None
        if pd.notna(row['end_date']) and str(row['end_date']).strip():
            end_date = str(row['end_date']).strip()
        
        item = {
            'id': f'work_{idx+1:03d}',
            'type': 'work_experience',
            'job_title': str(row['job_title']).strip(),
            'company_name': str(row['company_name']).strip(),
            'start_date': str(row['start_date']).strip(),
            'end_date': end_date,
            'is_current': is_current,
            'description': str(row['description']).strip() if pd.notna(row['description']) else '',
            'accomplishments': accomplishments
        }
        items.append(item)
    
    return items

def load_education(df):
    """Transform education data from DataFrame to DynamoDB format"""
    items = []
    
    for idx, row in df.iterrows():
        # Skip empty rows
        if pd.isna(row['degree']) or pd.isna(row['institution']):
            continue
        
        item = {
            'id': f'edu_{idx+1:03d}',
            'type': 'education',
            'degree': str(row['degree']).strip(),
            'institution': str(row['institution']).strip(),
            'start_date': str(row['start_date']).strip(),
            'end_date': str(row['end_date']).strip(),
            'description': str(row['description']).strip() if pd.notna(row['description']) else ''
        }
        items.append(item)
    
    return items

def load_skills(df):
    """Transform skills data from DataFrame to DynamoDB format"""
    items = []
    
    for idx, row in df.iterrows():
        # Skip empty rows
        if pd.isna(row['category']) or pd.isna(row['skills']):
            continue
        
        # Parse skills (pipe-separated)
        skills = [s.strip() for s in str(row['skills']).split('|')]
        
        # Get sort_order
        sort_order = 999
        if pd.notna(row['sort_order']):
            try:
                sort_order = int(row['sort_order'])
            except:
                sort_order = 999
        
        item = {
            'id': f'skills_{idx+1:03d}',
            'type': 'skills',
            'category': str(row['category']).strip(),
            'skills': skills,
            'sort_order': sort_order
        }
        items.append(item)
    
    return items

def load_profile(df):
    """Transform profile data from DataFrame to DynamoDB format"""
    # Profile is stored as key-value pairs in the sheet
    profile_data = {
        'id': 'profile',
        'type': 'profile'
    }
    
    # Read field/value pairs and build profile object
    for idx, row in df.iterrows():
        if pd.notna(row['field']) and pd.notna(row['value']):
            field = str(row['field']).strip()
            value = str(row['value']).strip()
            profile_data[field] = value
    
    return [profile_data]

def get_dynamodb_table():
    """Get DynamoDB table connection"""
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=os.getenv('AWS_ENDPOINT_URL', 'http://localhost:4566'),
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
    )
    return dynamodb.Table('ResumeData')

def clear_table(table):
    """Delete all items from DynamoDB table"""
    print("🗑️  Clearing existing data...")
    
    # Scan all items
    response = table.scan()
    items = response.get('Items', [])
    
    # Handle pagination
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
    
    # Delete all items
    with table.batch_writer() as batch:
        for item in items:
            batch.delete_item(Key={'id': item['id']})
    
    print(f"  ✓ Deleted {len(items)} items")

def write_to_dynamodb(table, items):
    """Write items to DynamoDB"""
    # Write items in batches for speed
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)
            item_type = item['type']
            item_name = item.get('job_title') or item.get('degree') or item.get('category', 'Unknown')
            print(f"  ✓ Added {item_type}: {item_name}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python load_resume.py <excel_file>")
        print("Example: python load_resume.py resume-data-template.xlsx")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    
    if not Path(excel_file).exists():
        print(f"Error: File '{excel_file}' not found")
        sys.exit(1)
    
    print(f"\n📊 Loading resume data from: {excel_file}\n")
    
    # Read Excel file
    try:
        profile_df = pd.read_excel(excel_file, sheet_name='Profile')
        work_df = pd.read_excel(excel_file, sheet_name='WorkExperience')
        edu_df = pd.read_excel(excel_file, sheet_name='Education')
        skills_df = pd.read_excel(excel_file, sheet_name='Skills')
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        sys.exit(1)
    
    # Transform data
    print("📝 Processing data...\n")
    profile_items = load_profile(profile_df)
    work_items = load_work_experience(work_df)
    edu_items = load_education(edu_df)
    skills_items = load_skills(skills_df)
    
    total_items = len(profile_items) + len(work_items) + len(edu_items) + len(skills_items)
    
    if total_items == 0:
        print("⚠️  No data found in Excel file")
        sys.exit(1)
    
    print(f"Found:")
    print(f"  - {len(profile_items)} profile")
    print(f"  - {len(work_items)} work experience entries")
    print(f"  - {len(edu_items)} education entries")
    print(f"  - {len(skills_items)} skill categories")
    print()
    
    # Get DynamoDB table
    try:
        table = get_dynamodb_table()
    except Exception as e:
        print(f"\n❌ Error connecting to DynamoDB: {e}")
        sys.exit(1)
    
    # Clear existing data
    try:
        clear_table(table)
    except Exception as e:
        print(f"\n❌ Error clearing table: {e}")
        sys.exit(1)
    
    print(f"\n💾 Writing to DynamoDB...\n")
    
    # Write to DynamoDB
    try:
        write_to_dynamodb(table, profile_items)
        write_to_dynamodb(table, work_items)
        write_to_dynamodb(table, edu_items)
        write_to_dynamodb(table, skills_items)
    except Exception as e:
        print(f"\n❌ Error writing to DynamoDB: {e}")
        sys.exit(1)
    
    print(f"\n✅ Successfully loaded {total_items} items into DynamoDB!\n")

if __name__ == '__main__':
    main()