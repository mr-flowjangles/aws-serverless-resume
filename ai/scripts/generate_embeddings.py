#!/usr/bin/env python3
"""
Generate Embeddings for RobbAI
Reads resume data from DynamoDB and personal info from YAML,
generates embeddings, and stores in ChatbotRAG table.
"""
import os
import sys
import json
import boto3
import yaml
from openai import OpenAI
from pathlib import Path
from decimal import Decimal

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_dynamodb_connection():
    """Get DynamoDB connection (works with LocalStack or AWS)"""
    endpoint_url = os.getenv('AWS_ENDPOINT_URL', 'http://localhost:4566')
    
    if endpoint_url == "":
        # Real AWS
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    else:
        # LocalStack
        dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=endpoint_url,
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
        )
    return dynamodb

def load_resume_data():
    """Load all resume data from DynamoDB"""
    print("Loading resume data from DynamoDB...")
    
    dynamodb = get_dynamodb_connection()
    table = dynamodb.Table('ResumeData')
    
    response = table.scan()
    items = response.get('Items', [])
    
    # Handle pagination
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
    
    print(f"  ✓ Loaded {len(items)} items from ResumeData")
    return items

def load_personal_info():
    """Load personal info from YAML file"""
    print("Loading personal info from config...")
    
    personal_info_path = Path('/app/ai/data/personal-info.yml')
    
    if not personal_info_path.exists():
        print("Personal info file not found, skipping")
        return None
    
    with open(personal_info_path, 'r') as f:
        personal_info = yaml.safe_load(f)
    
    print("Loaded personal info")
    return personal_info

def chunk_profile(item):
    """Convert profile item to text chunk"""
    text_parts = []
    
    # Basic info
    text_parts.append(f"Name: {item.get('name', 'Unknown')}")
    text_parts.append(f"Title: {item.get('title', 'Unknown')}")
    text_parts.append(f"Location: {item.get('location', 'Unknown')}")
    
    # Contact
    if 'linkedin' in item:
        text_parts.append(f"LinkedIn: {item['linkedin']}")
    if 'github' in item:
        text_parts.append(f"GitHub: {item['github']}")
    
    # Summary
    if 'summary' in item:
        text_parts.append(f"\nSummary: {item['summary']}")
    
    if 'professional_summary' in item:
        text_parts.append(f"\nProfessional Summary: {item['professional_summary']}")
    
    return "\n".join(text_parts)

def chunk_work_experience(item):
    """Convert work experience item to text chunk"""
    text_parts = []
    
    # Job header
    job_title = item.get('job_title', 'Unknown Position')
    company = item.get('company_name', 'Unknown Company')
    start_date = item.get('start_date', 'Unknown')
    end_date = item.get('end_date', 'Present') if item.get('is_current') else item.get('end_date', 'Unknown')
    
    text_parts.append(f"Position: {job_title} at {company}")
    text_parts.append(f"Duration: {start_date} to {end_date}")
    
    # Description
    if 'description' in item and item['description']:
        text_parts.append(f"\nDescription: {item['description']}")
    
    # Accomplishments
    if 'accomplishments' in item and item['accomplishments']:
        text_parts.append("\nKey Accomplishments:")
        for acc in item['accomplishments']:
            text_parts.append(f"- {acc}")
    
    return "\n".join(text_parts)

def chunk_education(item):
    """Convert education item to text chunk"""
    text_parts = []
    
    degree = item.get('degree', 'Unknown Degree')
    institution = item.get('institution', 'Unknown Institution')
    start_date = item.get('start_date', 'Unknown')
    end_date = item.get('end_date', 'Unknown')
    
    text_parts.append(f"Degree: {degree}")
    text_parts.append(f"Institution: {institution}")
    text_parts.append(f"Duration: {start_date} to {end_date}")
    
    if 'description' in item and item['description']:
        text_parts.append(f"Location: {item['description']}")
    
    return "\n".join(text_parts)

def chunk_skills(item):
    """Convert skills item to text chunk"""
    text_parts = []
    
    category = item.get('category', 'Unknown Category')
    skills = item.get('skills', [])
    
    text_parts.append(f"Skill Category: {category}")
    text_parts.append(f"Skills: {', '.join(skills)}")
    
    return "\n".join(text_parts)

def chunk_personal_info(personal_info):
    """Convert personal info to text chunks"""
    chunks = []
    
    if not personal_info:
        return chunks
    
    # About section
    if 'about' in personal_info:
        about = personal_info['about']
        text_parts = ["Personal Background:"]
        
        if 'hometown' in about:
            text_parts.append(f"Hometown: {about['hometown']}")
        if 'current_location' in about:
            text_parts.append(f"Current Location: {about['current_location']}")
        if 'background' in about:
            text_parts.append(f"\nBackground: {about['background']}")
        if 'family' in about:
            text_parts.append(f"\nFamily: {about['family']}")
        if 'fun_facts' in about:
            text_parts.append("\nFun Facts:")
            for fact in about['fun_facts']:
                if fact and not fact.startswith('TBD'):
                    text_parts.append(f"- {fact}")
        
        chunks.append({
            'type': 'personal_about',
            'text': "\n".join(text_parts),
            'source': 'personal_info'
        })
    
    # Hobbies section
    if 'hobbies' in personal_info:
        hobbies = personal_info['hobbies']
        
        for hobby_name, hobby_data in hobbies.items():
            if hobby_name == 'other':
                # Handle list of other hobbies
                if hobby_data:
                    other_text = "Other Hobbies:\n" + "\n".join([f"- {h}" for h in hobby_data if not h.startswith('TBD')])
                    chunks.append({
                        'type': 'personal_hobbies',
                        'text': other_text,
                        'source': 'personal_info'
                    })
            elif isinstance(hobby_data, dict):
                # Individual hobby with description and details
                text_parts = [f"Hobby: {hobby_name.title()}"]
                if 'description' in hobby_data and not hobby_data['description'].startswith('TBD'):
                    text_parts.append(f"Description: {hobby_data['description']}")
                if 'details' in hobby_data and not hobby_data['details'].startswith('TBD'):
                    text_parts.append(f"Details: {hobby_data['details']}")
                
                if len(text_parts) > 1:  # Only add if has real content
                    chunks.append({
                        'type': 'personal_hobbies',
                        'text': "\n".join(text_parts),
                        'source': 'personal_info'
                    })
    
    # Values section
    if 'values' in personal_info:
        values = personal_info['values']
        text_parts = ["Professional Values & Philosophy:"]
        
        for key, value in values.items():
            if value and not str(value).startswith('TBD'):
                field_name = key.replace('_', ' ').title()
                text_parts.append(f"\n{field_name}: {value}")
        
        if len(text_parts) > 1:  # Only add if has real content
            chunks.append({
                'type': 'personal_values',
                'text': "\n".join(text_parts),
                'source': 'personal_info'
            })
    
    # Career section
    if 'career' in personal_info:
        career = personal_info['career']
        text_parts = ["Career Information:"]
        
        if 'current_status' in career:
            text_parts.append(f"Current Status: {career['current_status']}")
        if 'interested_in' in career:
            text_parts.append(f"\nInterested in: {', '.join(career['interested_in'])}")
        if 'strengths' in career:
            text_parts.append(f"\nKey Strengths: {', '.join(career['strengths'])}")
        if 'learning_goals' in career:
            goals = [g for g in career['learning_goals'] if not g.startswith('TBD')]
            if goals:
                text_parts.append(f"\nLearning Goals: {', '.join(goals)}")
        
        chunks.append({
            'type': 'personal_career',
            'text': "\n".join(text_parts),
            'source': 'personal_info'
        })
    
    return chunks

def create_chunks(resume_data, personal_info):
    """Create text chunks from all data"""
    print("\n✂️  Creating chunks from data...")
    
    chunks = []
    
    # Process resume data
    for item in resume_data:
        item_type = item.get('type')
        chunk_text = None
        
        if item_type == 'profile':
            chunk_text = chunk_profile(item)
        elif item_type == 'work_experience':
            chunk_text = chunk_work_experience(item)
        elif item_type == 'education':
            chunk_text = chunk_education(item)
        elif item_type == 'skills':
            chunk_text = chunk_skills(item)
        
        if chunk_text:
            chunks.append({
                'id': item.get('id'),
                'type': item_type,
                'text': chunk_text,
                'source': 'resume',
                'metadata': item
            })
    
    print(f"  ✓ Created {len(chunks)} chunks from resume data")
    
    # Process personal info
    personal_chunks = chunk_personal_info(personal_info)
    
    # Add IDs to personal chunks
    for idx, chunk in enumerate(personal_chunks):
        chunk['id'] = f"personal_{idx+1:03d}"
    
    chunks.extend(personal_chunks)
    
    if personal_chunks:
        print(f"  ✓ Created {len(personal_chunks)} chunks from personal info")
    
    print(f"\n   Total chunks: {len(chunks)}")
    
    return chunks

def generate_embedding(text):
    """Generate embedding vector for text using OpenAI"""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def generate_embeddings(chunks):
    """Generate embeddings for all chunks"""
    print("\n🤖 Generating embeddings with OpenAI...")
    
    for idx, chunk in enumerate(chunks, 1):
        print(f"  [{idx}/{len(chunks)}] Generating embedding for {chunk['type']}: {chunk['id']}")
        
        try:
            embedding = generate_embedding(chunk['text'])
            chunk['embedding'] = embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            sys.exit(1)
    
    print(f"  ✓ Generated {len(chunks)} embeddings")
    return chunks

def store_in_dynamodb(chunks):
    """Store chunks with embeddings in ChatbotRAG table"""
    print("\n💾 Storing embeddings in ChatbotRAG table...")
    
    dynamodb = get_dynamodb_connection()
    table = dynamodb.Table('ChatbotRAG')
    
    # Clear existing data
    print("  🗑️  Clearing existing embeddings...")
    response = table.scan()
    existing_items = response.get('Items', [])
    
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        existing_items.extend(response.get('Items', []))
    
    with table.batch_writer() as batch:
        for item in existing_items:
            batch.delete_item(Key={'id': item['id']})
    
    if existing_items:
        print(f"    ✓ Deleted {len(existing_items)} existing items")
    
    # Store new embeddings
    print("Writing new embeddings...")
    
    with table.batch_writer() as batch:
        for chunk in chunks:
            item = {
                'id': chunk['id'],
                'type': chunk['type'],
                'text': chunk['text'],
                'embedding': [Decimal(str(x)) for x in chunk['embedding']],
                'source': chunk.get('source', 'resume')
            }
            
            # Add metadata if available
            if 'metadata' in chunk:
                # Store relevant metadata (but not the full item to avoid duplication)
                if chunk['type'] == 'work_experience':
                    item['company'] = chunk['metadata'].get('company_name')
                    item['job_title'] = chunk['metadata'].get('job_title')
                elif chunk['type'] == 'skills':
                    item['category'] = chunk['metadata'].get('category')
            
            batch.put_item(Item=item)
            print(f"Stored {chunk['type']}: {chunk['id']}")
    
    print(f"\nSuccessfully stored {len(chunks)} embeddings in ChatbotRAG!")

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("  RobbAI Embeddings Generator")
    print("="*60 + "\n")
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("   Please set your OpenAI API key in .env file")
        sys.exit(1)
    
    # Check if embeddings already exist BEFORE doing anything expensive
    print("Checking if embeddings already exist...")
    try:
        dynamodb = get_dynamodb_connection()
        table = dynamodb.Table('ChatbotRAG')
        response = table.scan(Limit=1)
        
        if response.get('Items'):
            print("  ✓ Embeddings already exist, skipping generation")
            print("  💡 To regenerate, delete the ChatbotRAG table first")
            print("\n" + "="*60)
            print("  ✅ Nothing to do - embeddings exist!")
            print("="*60 + "\n")
            return
    except Exception as e:
        print(f"  ChatbotRAG table not found or error: {e}")
        print("  Will proceed with embedding generation...")
    
    print("  📝 No embeddings found, generating new ones...\n")
    
    try:
        # Load data
        resume_data = load_resume_data()
        personal_info = load_personal_info()
        
        # Create chunks
        chunks = create_chunks(resume_data, personal_info)
        
        # Generate embeddings
        chunks_with_embeddings = generate_embeddings(chunks)
        
        # Store in DynamoDB
        store_in_dynamodb(chunks_with_embeddings)
        
        print("\n" + "="*60)
        print("  ✅ Embeddings generation complete!")
        print("="*60 + "\n")
        
        print(f"Summary:")
        print(f"  - Resume chunks: {len([c for c in chunks if c.get('source') == 'resume'])}")
        print(f"  - Personal chunks: {len([c for c in chunks if c.get('source') == 'personal_info'])}")
        print(f"  - Total embeddings: {len(chunks)}")
        print(f"  - Stored in: ChatbotRAG table")
        print()
        
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()