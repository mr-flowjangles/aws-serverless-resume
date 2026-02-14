"""
Chunker Module

Reads YAML files in the universal bot data format and produces
text chunks ready for embedding generation.

Handles two format types:
  - "text": content is already readable text, pass through as-is
  - "structured": apply the template string to each item to produce text

Input:  bot_id string (resolves to bots/{bot_id}/data/ folder)
Output: List of dicts with {id, bot_id, category, heading, text}
"""
import yaml
from pathlib import Path


def get_bot_data_path(bot_id: str) -> Path:
    """Resolve the data folder path for a given bot."""
    return Path(__file__).parent.parent / 'bots' / bot_id / 'data'


def load_yaml_files(data_path: Path) -> list[dict]:
    """
    Load all .yml files from a bot's data folder.
    Returns the combined list of entries from all files.
    """
    all_entries = []

    if not data_path.exists():
        print(f"  Warning: data folder not found at {data_path}")
        return all_entries

    yml_files = sorted(data_path.glob('*.yml'))

    if not yml_files:
        print(f"  Warning: no .yml files found in {data_path}")
        return all_entries

    for yml_file in yml_files:
        print(f"  Reading {yml_file.name}...")
        with open(yml_file, 'r') as f:
            data = yaml.safe_load(f)

        entries = data.get('entries', [])
        all_entries.extend(entries)
        print(f"    Found {len(entries)} entries")

    return all_entries


def chunk_text_entry(entry: dict) -> str:
    """
    Process a 'text' format entry.
    Content is already readable — combine heading + content.
    """
    heading = entry.get('heading', '')
    content = entry.get('content', '')

    if heading and content:
        return f"{heading}\n\n{content}"
    return content or heading


def chunk_structured_entry(entry: dict) -> str:
    """
    Process a 'structured' format entry.
    Apply the template to each item, then combine with heading.
    """
    heading = entry.get('heading', '')
    template = entry.get('template', '')
    items = entry.get('items', [])

    if not template or not items:
        print(f"  Warning: structured entry '{entry.get('id')}' missing template or items")
        return heading

    # Apply template to each item
    parts = [heading] if heading else []

    for item in items:
        try:
            text = template.format(**item)
            parts.append(text)
        except KeyError as e:
            print(f"  Warning: template placeholder {e} not found in item for entry '{entry.get('id')}'")
            continue

    return '\n'.join(parts)


def chunk_entry(entry: dict) -> str:
    """Route an entry to the correct chunker based on its format."""
    fmt = entry.get('format', 'text')

    # Accept aliases
    if fmt in ('text', 'string'):
        return chunk_text_entry(entry)
    elif fmt in ('structured', 'object'):
        return chunk_structured_entry(entry)
    else:
        print(f"  Warning: unknown format '{fmt}' for entry '{entry.get('id')}', treating as text")
        return chunk_text_entry(entry)


def load_bot_data(bot_id: str) -> list[dict]:
    """
    Main entry point. Load and chunk all data for a bot.

    Returns a list of dicts ready for embedding:
        {id, bot_id, category, heading, text}
    """
    print(f"Loading data for bot: {bot_id}")

    data_path = get_bot_data_path(bot_id)
    entries = load_yaml_files(data_path)

    if not entries:
        print(f"  No entries found for bot '{bot_id}'")
        return []

    chunks = []
    for entry in entries:
        text = chunk_entry(entry)

        if not text or not text.strip():
            print(f"  Skipping empty entry: {entry.get('id')}")
            continue

        chunks.append({
            'id': entry['id'],
            'bot_id': bot_id,
            'category': entry.get('category', 'General'),
            'heading': entry.get('heading', ''),
            'text': text
        })

    print(f"  Produced {len(chunks)} chunks for bot '{bot_id}'")
    return chunks
