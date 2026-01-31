# Generate Embeddings - Instructions

## Prerequisites

1. **OpenAI API Key**
   - Sign up at https://platform.openai.com
   - Create API key at https://platform.openai.com/api-keys
   - Copy the key (starts with `sk-...`)

2. **Add to .env file**

   ```bash
   # Add this line to your .env file
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

3. **Install Dependencies**
   The AI container needs additional Python packages.

   **Option A: Add to main requirements.txt**

   ```bash
   # Add these to api/requirements.txt:
   openai>=1.0.0
   pyyaml>=6.0
   numpy>=1.24.0
   scipy>=1.11.0
   ```

   **Option B: Separate AI requirements** (recommended for isolation)

   ```bash
   # Save ai-requirements.txt to ai/ folder
   # Install in container:
   docker exec -it resume-api-1 pip install -r /app/ai/requirements.txt
   ```

## Usage

### Step 1: Resume Data

Make Sure Data is Loaded

### Step 2: Fill Out Personal Info (Optional)

Edit `ai/data/personal-info.yml` and replace all the "TBD" placeholders with your actual information.

If you skip this, the script will only generate embeddings for your resume data.

### Step 3: Generate Embeddings

```bash
# Run the embeddings generator
docker exec -it resume-api-1 python /app/ai/scripts/generate_embeddings.py
```

## What It Does

1. **Reads Resume Data** from DynamoDB (ResumeData table)
2. **Reads Personal Info** from ai/data/personal-info.yml
3. **Creates Chunks** - Converts each item to text
   - Profile → 1 chunk
   - Each work experience → 1 chunk
   - Each education → 1 chunk
   - Each skill category → 1 chunk
   - Personal sections → Multiple chunks
4. **Generates Embeddings** - Converts each chunk to a 1536-dimension vector using OpenAI
5. **Stores in DynamoDB** - Saves to ChatbotRAG table

## Output Example

```
==============================================================
  RobbAI Embeddings Generator
==============================================================

📊 Loading resume data from DynamoDB...
  ✓ Loaded 12 items from ResumeData

📝 Loading personal info from config...
  ✓ Loaded personal info

✂️  Creating chunks from data...
  ✓ Created 12 chunks from resume data
  ✓ Created 5 chunks from personal info

  📦 Total chunks: 17

🤖 Generating embeddings with OpenAI...
  [1/17] Generating embedding for profile: profile
  [2/17] Generating embedding for work_experience: work_001
  ...
  ✓ Generated 17 embeddings

💾 Storing embeddings in ChatbotRAG table...
  🗑️  Clearing existing embeddings...
  📝 Writing new embeddings...
    ✓ Stored profile: profile
    ✓ Stored work_experience: work_001
    ...

==============================================================
  ✅ Embeddings generation complete!
==============================================================

Summary:
  - Resume chunks: 12
  - Personal chunks: 5
  - Total embeddings: 17
  - Stored in: ChatbotRAG table
```

## Troubleshooting

### "OPENAI_API_KEY environment variable not set"

- Make sure you added the key to your .env file
- Restart the container: `docker-compose restart api`

### "ModuleNotFoundError: No module named 'openai'"

- Install dependencies: `docker exec -it resume-api-1 pip install openai pyyaml numpy scipy`

### "Table 'ChatbotRAG' not found"

- Make sure chatbot is enabled in ai/config.yml
- Run the init script: `docker exec -it resume-api-1 bash /app/ai/scripts/init-chatbot-table.sh`

## Cost

- **Embeddings generation**: ~$0.01 per run (for ~20 chunks)
- **Your $5 free credit**: Can regenerate 500+ times
- **Tiny cost**: This is not expensive!

## When to Regenerate

Run this script whenever you:

- Update your resume data
- Change your personal info
- Want to refresh the embeddings

The script clears old embeddings and creates fresh ones each time.
