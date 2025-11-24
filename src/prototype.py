"""
Prototype: End-to-end reporter information extraction
Tests: Google Search → Grok Extraction → Confidence Scoring
"""

import sys
import io
from pathlib import Path
import json

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
    print(f"\n[1] Searching Google for: '{query}'")

    try:
        service = build("customsearch", "v1", developerKey=Config.GOOGLE_API_KEY)
        result = service.cse().list(
            q=query,
            cx=Config.GOOGLE_SEARCH_ENGINE_ID,
            num=num_results
        ).execute()

        if 'items' not in result:
            print("[!] No search results found")
            return []

        results = []
        for item in result['items']:
            results.append({
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'snippet': item.get('snippet', '')
            })
            print(f"  - {item.get('title', 'No title')}")

        return results

    except Exception as e:
        print(f"[X] Google Search Error: {e}")
        return []

def extract_with_grok(reporter_name, search_results):
    """Use Grok to extract structured reporter information from search results"""
    print(f"\n[2] Extracting information with Grok...")

    # Prepare search context for Grok
    context = f"Reporter Name: {reporter_name}\n\nSearch Results:\n"
    for i, result in enumerate(search_results, 1):
        context += f"\n{i}. {result['title']}\n{result['snippet']}\nURL: {result['link']}\n"

    # Grok extraction prompt
    prompt = f"""You are analyzing search results for an Israeli media professional.

{context}

Task: Extract the following information about "{reporter_name}":
- Full Name (Hebrew and English if available)
- Current Job Title
- Current Employer/Organization
- Contact Email (if found)
- Phone/Mobile (if found)
- Professional Topics/Beats (journalism focus areas)

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
  "sources_found": ["list of sources"],
  "notes": "any important observations"
}}

Confidence Score Guidelines:
- 90-100: Multiple reliable sources agree, all key fields found
- 70-89: One reliable source, most key fields found
- 50-69: Partial information, uncertain sources
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
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=1000
        )

        response = completion.choices[0].message.content.strip()

        # Parse JSON response
        # Remove markdown code blocks if present
        if response.startswith("```"):
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
            response = response.strip()

        data = json.loads(response)

        print(f"[OK] Extracted data with {data.get('confidence_score', 0)}% confidence")
        return data

    except Exception as e:
        print(f"[X] Grok Extraction Error: {e}")
        return None

def prototype_test(reporter_name_hebrew, reporter_name_english=None):
    """
    End-to-end prototype test

    Args:
        reporter_name_hebrew: Hebrew name from CSV
        reporter_name_english: Optional English transliteration
    """
    print("=" * 70)
    print("Reporter Database Updater - Prototype Test")
    print("=" * 70)
    print(f"\nTesting with: {reporter_name_hebrew}")
    if reporter_name_english:
        print(f"English: {reporter_name_english}")

    # Step 1: Search Google
    # Try Hebrew name first, then English if available
    search_queries = [
        f'"{reporter_name_hebrew}" reporter Israel journalist',
    ]
    if reporter_name_english:
        search_queries.append(f'"{reporter_name_english}" reporter Israel journalist')

    all_results = []
    for query in search_queries:
        results = search_google(query, num_results=3)
        all_results.extend(results)
        if len(all_results) >= 5:  # Enough results
            break

    if not all_results:
        print("\n[!] No search results found. Cannot proceed.")
        return None

    # Step 2: Extract with Grok
    extracted_data = extract_with_grok(reporter_name_hebrew, all_results[:5])

    if not extracted_data:
        print("\n[!] Extraction failed. Cannot proceed.")
        return None

    # Step 3: Display results
    print("\n" + "=" * 70)
    print("Extraction Results")
    print("=" * 70)
    print(json.dumps(extracted_data, indent=2, ensure_ascii=False))

    # Step 4: Decision
    confidence = extracted_data.get('confidence_score', 0)
    print("\n" + "=" * 70)
    print("Decision")
    print("=" * 70)

    if confidence >= Config.CONFIDENCE_THRESHOLD:
        print(f"[OK] Confidence: {confidence}% >= {Config.CONFIDENCE_THRESHOLD}%")
        print("[OK] Decision: AUTO-UPDATE")
    else:
        print(f"[!] Confidence: {confidence}% < {Config.CONFIDENCE_THRESHOLD}%")
        print("[!] Decision: MANUAL REVIEW QUEUE")

    return extracted_data

if __name__ == "__main__":
    # Test with Avi Weiss from the sample CSV (row 2)
    # Hebrew: אבי וייס
    # Known employer: ch2news.tv (Channel 2)
    # Known role: CEO, Chief Editor

    result = prototype_test(
        reporter_name_hebrew="אבי וייס",
        reporter_name_english="Avi Weiss"
    )

    if result:
        print("\n[OK] Prototype test completed successfully!")
    else:
        print("\n[X] Prototype test failed!")
