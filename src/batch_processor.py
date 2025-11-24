"""
Batch processor: Process multiple reporters and update CSV
"""

import sys
import io
from pathlib import Path
import json
import pandas as pd
from datetime import datetime
import time

# Fix Windows console encoding for Hebrew
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from googleapiclient.discovery import build
from openai import OpenAI

def search_google(query, num_results=5):
    """Search Google and return top results"""
    try:
        service = build("customsearch", "v1", developerKey=Config.GOOGLE_API_KEY)
        result = service.cse().list(
            q=query,
            cx=Config.GOOGLE_SEARCH_ENGINE_ID,
            num=num_results
        ).execute()

        if 'items' not in result:
            return []

        results = []
        for item in result['items']:
            results.append({
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'snippet': item.get('snippet', '')
            })
        return results

    except Exception as e:
        print(f"  [X] Search error: {e}")
        return []

def extract_with_grok(reporter_name, search_results):
    """Use Grok to extract structured reporter information"""
    context = f"Reporter Name: {reporter_name}\n\nSearch Results:\n"
    for i, result in enumerate(search_results, 1):
        context += f"\n{i}. {result['title']}\n{result['snippet']}\nURL: {result['link']}\n"

    prompt = f"""You are analyzing search results for an Israeli media professional.

{context}

Task: Extract the following information about "{reporter_name}":
- Full Name (Hebrew and English if available)
- Current Job Title (in Hebrew if possible)
- Current Employer/Organization (in Hebrew if possible)
- Contact Email (search carefully in all results, check author info, contact sections)
- Phone/Mobile (search carefully in all results, look for contact information)
- Professional Topics/Beats (in Hebrew if possible)

IMPORTANT: For Israeli media professionals, prefer Hebrew for all fields except email/phone/URLs.

Search CAREFULLY for email and phone in:
- Author bio sections
- Contact information in articles
- "About the author" sections
- Staff directory listings
- Profile pages

Return ONLY a JSON object with this exact structure (use null for missing fields):
{{
  "name_hebrew": "...",
  "name_english": "...",
  "job_title": "...",
  "employer": "...",
  "email": "...",
  "phone": "...",
  "topics": "...",
  "confidence_score": 0-100,
  "source_urls": ["url1", "url2", "url3"],
  "notes": "any important observations about what you found and where"
}}

Confidence Score Guidelines:
- 90-100: Multiple reliable sources agree, all key fields found including contact info
- 70-89: One reliable source, most key fields found, some contact info
- 50-69: Partial information, uncertain sources, missing contact info
- Below 50: Very limited or no relevant information

IMPORTANT: Return ONLY the JSON object, no other text."""

    try:
        client = OpenAI(
            api_key=Config.GROK_API_KEY,
            base_url=Config.GROK_BASE_URL
        )

        completion = client.chat.completions.create(
            model=Config.GROK_MODEL,
            messages=[
                {"role": "system", "content": "You are a data extraction assistant. Return only valid JSON, no other text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1000
        )

        response = completion.choices[0].message.content.strip()

        # Remove markdown code blocks if present
        if response.startswith("```"):
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
            response = response.strip()

        data = json.loads(response)
        return data

    except Exception as e:
        print(f"  [X] Extraction error: {e}")
        return None

def process_reporter(row_index, first_name, last_name):
    """Process a single reporter"""
    full_name_hebrew = f"{first_name} {last_name}"

    print(f"\n{'='*70}")
    print(f"Processing #{row_index}: {full_name_hebrew}")
    print('='*70)

    # Search with Hebrew name
    query = f'"{full_name_hebrew}" Israel journalist reporter media'
    print(f"  [1] Searching Google...")
    results = search_google(query, num_results=5)

    if not results:
        print(f"  [!] No results found")
        return None

    print(f"  [OK] Found {len(results)} results")

    # Extract with Grok
    print(f"  [2] Extracting with Grok...")
    extracted = extract_with_grok(full_name_hebrew, results)

    if not extracted:
        print(f"  [!] Extraction failed")
        return None

    confidence = extracted.get('confidence_score', 0)
    print(f"  [OK] Confidence: {confidence}%")

    decision = "AUTO-UPDATE" if confidence >= Config.CONFIDENCE_THRESHOLD else "MANUAL REVIEW"
    print(f"  [OK] Decision: {decision}")

    return extracted

def batch_process(num_reporters=5, start_row=2):
    """
    Process multiple reporters and update CSV

    Args:
        num_reporters: Number of reporters to process
        start_row: Starting row index (2 = first reporter after header)
    """
    print("="*70)
    print("Reporter Database Updater - Batch Processing")
    print("="*70)
    print(f"Processing {num_reporters} reporters starting from row {start_row}")

    # Read CSV
    print(f"\nReading CSV: {Config.DB_SAMPLE_PATH}")
    df = pd.read_csv(Config.DB_SAMPLE_PATH, encoding='utf-8')

    print(f"[OK] Loaded {len(df)} reporters")
    print(f"[OK] Columns: {list(df.columns)}")

    # Add new columns for tracking
    if 'confidence_score' not in df.columns:
        df['confidence_score'] = None
    if 'last_updated' not in df.columns:
        df['last_updated'] = None
    if 'update_notes' not in df.columns:
        df['update_notes'] = None
    if 'decision' not in df.columns:
        df['decision'] = None
    if 'source_urls' not in df.columns:
        df['source_urls'] = None
    if 'search_history' not in df.columns:
        df['search_history'] = None

    # Process reporters
    results = []
    end_row = min(start_row + num_reporters, len(df))

    for i in range(start_row - 1, end_row - 1):  # -1 because pandas is 0-indexed
        row = df.iloc[i]
        first_name = row['שם פרטי']
        last_name = row['שם משפחה']

        # Process reporter
        extracted = process_reporter(i + 2, first_name, last_name)  # +2 for display (1 for header, 1 for 0-index)

        if extracted:
            # Update DataFrame
            confidence = extracted.get('confidence_score', 0)
            decision = "AUTO-UPDATE" if confidence >= Config.CONFIDENCE_THRESHOLD else "MANUAL REVIEW"

            # Only update if auto-update threshold met
            if decision == "AUTO-UPDATE":
                changes = []

                # Update job title/employer (תפקיד column)
                if extracted.get('job_title') or extracted.get('employer'):
                    old_val = str(row.get('תפקיד', ''))
                    employer = extracted.get('employer', '')
                    job_title = extracted.get('job_title', '')

                    # Combine employer and title
                    new_val = f"{job_title} @ {employer}" if employer and job_title else (job_title or employer)

                    if old_val != new_val and new_val:
                        df.at[i, 'תפקיד'] = new_val
                        changes.append(f"תפקיד: '{old_val}' → '{new_val}'")

                # Update topics (נושאים column)
                if extracted.get('topics'):
                    old_val = str(row.get('נושאים', ''))
                    new_val = extracted['topics']
                    if old_val != new_val and new_val != 'null':
                        df.at[i, 'נושאים'] = new_val
                        changes.append(f"נושאים: '{old_val}' → '{new_val}'")

                # Update email (דוא"ל column)
                if extracted.get('email'):
                    old_val = str(row.get('דוא"ל', ''))
                    new_val = extracted['email']
                    if old_val != new_val and new_val != 'null':
                        df.at[i, 'דוא"ל'] = new_val
                        changes.append(f"דוא\"ל: '{old_val}' → '{new_val}'")

                # Update mobile phone (נייד column)
                if extracted.get('phone'):
                    old_val = str(row.get('נייד', ''))
                    new_val = extracted['phone']
                    if old_val != new_val and new_val != 'null':
                        df.at[i, 'נייד'] = new_val
                        changes.append(f"נייד: '{old_val}' → '{new_val}'")

                if changes:
                    update_notes = "UPDATED: " + " | ".join(changes)
                else:
                    update_notes = f"No changes needed. Verified: {extracted.get('employer', 'N/A')} - {extracted.get('job_title', 'N/A')}"
            else:
                # For manual review, still record what we found
                found_info = []
                if extracted.get('employer'):
                    found_info.append(f"Employer: {extracted['employer']}")
                if extracted.get('job_title'):
                    found_info.append(f"Title: {extracted['job_title']}")
                if extracted.get('email'):
                    found_info.append(f"Email: {extracted['email']}")
                if extracted.get('phone'):
                    found_info.append(f"Phone: {extracted['phone']}")
                if extracted.get('topics'):
                    found_info.append(f"Topics: {extracted['topics']}")

                update_notes = f"Low confidence ({confidence}%). Found: " + "; ".join(found_info) if found_info else f"Low confidence. Needs manual verification."

            # Store source URLs
            source_urls = extracted.get('source_urls', [])
            df.at[i, 'source_urls'] = "; ".join(source_urls) if source_urls else None

            # Build search history entry
            timestamp = datetime.now().isoformat()
            history_entry = f"[{timestamp}] Confidence: {confidence}% | Decision: {decision} | {update_notes}"

            # Append to search history (keep all previous searches)
            existing_history = df.at[i, 'search_history']
            if pd.isna(existing_history) or existing_history == '':
                df.at[i, 'search_history'] = history_entry
            else:
                df.at[i, 'search_history'] = existing_history + " || " + history_entry

            df.at[i, 'confidence_score'] = confidence
            df.at[i, 'last_updated'] = timestamp
            df.at[i, 'update_notes'] = update_notes
            df.at[i, 'decision'] = decision

            results.append({
                'row': i + 2,
                'name': f"{first_name} {last_name}",
                'confidence': confidence,
                'decision': decision,
                'extracted': extracted
            })

        # Rate limiting: 1 second between requests
        if i < end_row - 2:
            print(f"\n  [~] Waiting 2 seconds (rate limiting)...")
            time.sleep(2)

    # Save updated CSV - OVERWRITE the original to keep history in same file
    output_path = Config.DB_SAMPLE_PATH

    # Also save a timestamped backup
    backup_path = Config.OUTPUT_PATH / f"backup_reporters_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    Config.OUTPUT_PATH.mkdir(exist_ok=True)

    df.to_csv(output_path, index=False, encoding='utf-8-sig')  # utf-8-sig for Excel compatibility
    df.to_csv(backup_path, index=False, encoding='utf-8-sig')  # Backup copy
    print(f"\n{'='*70}")
    print("Summary")
    print('='*70)
    print(f"[OK] Processed: {len(results)} reporters")
    print(f"[OK] Updated original CSV: {output_path}")
    print(f"[OK] Backup saved to: {backup_path}")

    # Display summary
    auto_updates = sum(1 for r in results if r['decision'] == 'AUTO-UPDATE')
    manual_reviews = sum(1 for r in results if r['decision'] == 'MANUAL REVIEW')

    print(f"\n  Auto-updates: {auto_updates}")
    print(f"  Manual reviews: {manual_reviews}")

    print(f"\nDetailed Results:")
    for r in results:
        print(f"  Row {r['row']}: {r['name']} - {r['confidence']}% - {r['decision']}")

    return results, output_path

if __name__ == "__main__":
    # Process 10 reporters starting from row 20 (we already tested rows 2-19)
    results, output_file = batch_process(num_reporters=10, start_row=20)

    print(f"\n[OK] Batch processing complete!")
    print(f"[OK] Updated CSV saved to: {output_file}")
