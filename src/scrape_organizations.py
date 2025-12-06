"""
Organization Staff Scraper
Scrapes journalist information from Israeli media organization websites
Uses Crawl4AI for extraction and Grok for Hebrew name processing
"""

import asyncio
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Optional
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config

# Check if crawl4ai is available
try:
    from crawl4ai import AsyncWebCrawler
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    print("[!] Crawl4AI not installed. Install with: pip install crawl4ai")

from openai import OpenAI


# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
ORGS_FILE = DATA_DIR / "media_organizations.json"
JOURNALISTS_FILE = DATA_DIR / "journalists.json"


def load_organizations() -> dict:
    """Load organizations from JSON file"""
    with open(ORGS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_journalists() -> dict:
    """Load journalists from JSON file"""
    with open(JOURNALISTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_journalists(data: dict):
    """Save journalists to JSON file"""
    data['metadata']['last_updated'] = datetime.now().isoformat()
    data['metadata']['total_journalists'] = len(data['journalists'])

    with open(JOURNALISTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] Saved {len(data['journalists'])} journalists to {JOURNALISTS_FILE}")


def generate_journalist_id(org_id: str, name: str) -> str:
    """Generate unique ID for journalist"""
    # Create slug from name
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'[\s]+', '-', slug)
    return f"{org_id}_{slug}"


async def scrape_with_crawl4ai(url: str, org_name: str) -> Optional[str]:
    """Scrape URL using Crawl4AI and return markdown content"""
    if not CRAWL4AI_AVAILABLE:
        print(f"[!] Crawl4AI not available, skipping {url}")
        return None

    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url)
            return result.markdown
    except Exception as e:
        print(f"[X] Error scraping {url}: {e}")
        return None


def extract_journalists_with_grok(content: str, org_name: str, org_id: str) -> list:
    """Use Grok to extract journalist information from scraped content"""

    # Split content into chunks if too long (process in batches)
    max_chunk_size = 25000
    all_journalists = []

    # Try to extract from different parts of the content
    chunks = []
    if len(content) > max_chunk_size:
        # Split into overlapping chunks
        for i in range(0, len(content), max_chunk_size - 2000):
            chunk = content[i:i + max_chunk_size]
            if len(chunk) > 1000:  # Only process meaningful chunks
                chunks.append(chunk)
    else:
        chunks = [content]

    print(f"  [*] Processing {len(chunks)} content chunk(s)...")

    for chunk_idx, chunk in enumerate(chunks):
        prompt = f"""You are analyzing a webpage from the Israeli news organization "{org_name}".

Extract ALL journalists, reporters, editors, anchors, columnists, correspondents, and media professionals mentioned.
Look for names in author lists, bylines, staff directories, team pages, and "about us" sections.

For EACH person found, extract:
- Full name in Hebrew (if available)
- Full name in English (transliteration)
- Job title/role (in Hebrew and/or English)
- Beat/topics they cover (politics, economy, sports, etc.)
- Email (if visible)
- Any profile URL mentioned

WEBPAGE CONTENT (chunk {chunk_idx + 1}/{len(chunks)}):
{chunk}

Return ONLY a JSON array of journalist objects. Each object should have:
{{
  "name_hebrew": "השם בעברית",
  "name_english": "Name in English",
  "job_title_hebrew": "תפקיד",
  "job_title_english": "Role",
  "beat": "topics covered",
  "email": "email@example.com or null",
  "profile_url": "url or null"
}}

If no journalists are found, return an empty array: []

Return ONLY the JSON array, no other text."""

        try:
            client = OpenAI(
                api_key=Config.GROK_API_KEY,
                base_url=Config.GROK_BASE_URL
            )

            completion = client.chat.completions.create(
                model=Config.GROK_MODEL,
                messages=[
                    {"role": "system", "content": "You are a data extraction assistant. Return only valid JSON arrays. Extract ALL people you find, do not limit the results."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=8000
            )

            response = completion.choices[0].message.content.strip()

            # Clean up response
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
                response = response.strip()

            chunk_journalists = json.loads(response)
            print(f"    [+] Chunk {chunk_idx + 1}: Found {len(chunk_journalists)} journalists")
            all_journalists.extend(chunk_journalists)

        except Exception as e:
            print(f"    [X] Chunk {chunk_idx + 1} error: {e}")
            continue

    # Deduplicate by name
    seen_names = set()
    unique_journalists = []
    for j in all_journalists:
        name_key = (j.get('name_english') or j.get('name_hebrew', '')).lower().strip()
        if name_key and name_key not in seen_names:
            seen_names.add(name_key)
            # Add metadata
            j['organization_id'] = org_id
            j['organization_name'] = org_name
            j['id'] = generate_journalist_id(org_id, j.get('name_english') or j.get('name_hebrew', 'unknown'))
            j['status'] = 'active'
            j['scraped_date'] = datetime.now().isoformat()
            j['confidence_score'] = 70  # Default confidence
            j['verified'] = False
            unique_journalists.append(j)

    return unique_journalists


async def scrape_organization(org: dict) -> list:
    """Scrape a single organization for journalist data"""
    org_id = org['id']
    org_name = org['name_english']
    staff_url = org.get('staff_page_url')
    website = org.get('website')

    print(f"\n{'='*60}")
    print(f"Scraping: {org_name} ({org_id})")
    print(f"{'='*60}")

    # Determine URL to scrape
    url = staff_url or website
    if not url:
        print(f"[!] No URL available for {org_name}")
        return []

    print(f"[1] Fetching: {url}")

    # Scrape the page
    content = await scrape_with_crawl4ai(url, org_name)

    if not content:
        print(f"[!] No content retrieved for {org_name}")
        return []

    print(f"[2] Retrieved {len(content)} characters")
    print(f"[3] Extracting journalists with Grok...")

    # Extract journalists
    journalists = extract_journalists_with_grok(content, org_name, org_id)

    # Add source URL
    for j in journalists:
        j['source_url'] = url

    print(f"[OK] Found {len(journalists)} journalists")

    return journalists


async def scrape_priority_organizations(priority: int = 1):
    """Scrape all organizations with given priority level"""
    orgs_data = load_organizations()
    journalists_data = load_journalists()

    # Filter by priority
    target_orgs = [
        org for org in orgs_data['organizations']
        if org.get('scraping_priority') == priority and org.get('status') == 'active'
    ]

    print(f"\n{'#'*60}")
    print(f"# Scraping Priority {priority} Organizations ({len(target_orgs)} total)")
    print(f"{'#'*60}")

    all_journalists = []

    for org in target_orgs:
        try:
            journalists = await scrape_organization(org)
            all_journalists.extend(journalists)

            # Rate limiting
            print("[~] Waiting 3 seconds...")
            await asyncio.sleep(3)

        except Exception as e:
            print(f"[X] Error processing {org['name_english']}: {e}")
            continue

    # Merge with existing journalists (avoid duplicates)
    existing_ids = {j['id'] for j in journalists_data['journalists']}
    new_journalists = [j for j in all_journalists if j['id'] not in existing_ids]

    journalists_data['journalists'].extend(new_journalists)

    # Save
    save_journalists(journalists_data)

    print(f"\n{'='*60}")
    print(f"SUMMARY: Priority {priority}")
    print(f"{'='*60}")
    print(f"Organizations scraped: {len(target_orgs)}")
    print(f"New journalists found: {len(new_journalists)}")
    print(f"Total journalists in DB: {len(journalists_data['journalists'])}")

    return new_journalists


async def scrape_single_organization(org_id: str):
    """Scrape a single organization by ID"""
    orgs_data = load_organizations()
    journalists_data = load_journalists()

    # Find organization
    org = next((o for o in orgs_data['organizations'] if o['id'] == org_id), None)

    if not org:
        print(f"[X] Organization not found: {org_id}")
        return []

    journalists = await scrape_organization(org)

    # Merge with existing
    existing_ids = {j['id'] for j in journalists_data['journalists']}
    new_journalists = [j for j in journalists if j['id'] not in existing_ids]

    journalists_data['journalists'].extend(new_journalists)
    save_journalists(journalists_data)

    return new_journalists


def list_organizations_by_priority():
    """Print organizations grouped by scraping priority"""
    orgs_data = load_organizations()

    for priority in [1, 2, 3]:
        orgs = [o for o in orgs_data['organizations'] if o.get('scraping_priority') == priority]
        print(f"\n{'='*60}")
        print(f"Priority {priority}: {len(orgs)} organizations")
        print(f"{'='*60}")
        for org in orgs:
            status = "✅" if org.get('staff_page_url') else "⚠️"
            print(f"  {status} {org['id']}: {org['name_english']}")


def get_scraping_stats():
    """Print current scraping statistics"""
    orgs_data = load_organizations()
    journalists_data = load_journalists()

    print(f"\n{'='*60}")
    print("SCRAPING STATISTICS")
    print(f"{'='*60}")
    print(f"Total organizations: {len(orgs_data['organizations'])}")
    print(f"Total journalists: {len(journalists_data['journalists'])}")

    # By organization
    org_counts = {}
    for j in journalists_data['journalists']:
        org = j.get('organization_name', 'Unknown')
        org_counts[org] = org_counts.get(org, 0) + 1

    if org_counts:
        print(f"\nJournalists by organization:")
        for org, count in sorted(org_counts.items(), key=lambda x: -x[1]):
            print(f"  {org}: {count}")


# CLI Interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scrape Israeli media organizations for journalist data")
    parser.add_argument('command', choices=['list', 'stats', 'scrape', 'scrape-all', 'scrape-priority'],
                       help='Command to run')
    parser.add_argument('--org', type=str, help='Organization ID to scrape')
    parser.add_argument('--priority', type=int, default=1, help='Priority level to scrape (1, 2, or 3)')

    args = parser.parse_args()

    if args.command == 'list':
        list_organizations_by_priority()

    elif args.command == 'stats':
        get_scraping_stats()

    elif args.command == 'scrape':
        if not args.org:
            print("Error: --org required for 'scrape' command")
        else:
            asyncio.run(scrape_single_organization(args.org))

    elif args.command == 'scrape-priority':
        asyncio.run(scrape_priority_organizations(args.priority))

    elif args.command == 'scrape-all':
        async def scrape_all():
            for p in [1, 2, 3]:
                await scrape_priority_organizations(p)
        asyncio.run(scrape_all())
