"""
Test script to verify API connections are working
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config

def test_google_search():
    """Test Google Custom Search API"""
    print("\n" + "="*50)
    print("Testing Google Custom Search API")
    print("="*50)

    try:
        from googleapiclient.discovery import build

        service = build("customsearch", "v1", developerKey=Config.GOOGLE_API_KEY)

        # Test search for a simple query
        result = service.cse().list(
            q="test",
            cx=Config.GOOGLE_SEARCH_ENGINE_ID,
            num=1
        ).execute()

        if 'items' in result:
            print("[OK] Google Search API is working!")
            print(f"[OK] Found {result['searchInformation']['totalResults']} results for 'test'")
            print(f"[OK] First result: {result['items'][0]['title']}")
            return True
        else:
            print("[!] Google Search API returned no results")
            return False

    except Exception as e:
        print(f"[X] Google Search API Error: {e}")
        return False

def test_grok_api():
    """Test Grok API connection"""
    print("\n" + "="*50)
    print("Testing Grok API")
    print("="*50)

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=Config.GROK_API_KEY,
            base_url=Config.GROK_BASE_URL
        )

        # Simple test completion
        completion = client.chat.completions.create(
            model=Config.GROK_MODEL,
            messages=[
                {"role": "user", "content": "Say 'API test successful' if you can read this."}
            ],
            max_tokens=20
        )

        response = completion.choices[0].message.content
        print(f"[OK] Grok API is working!")
        print(f"[OK] Response: {response}")
        return True

    except Exception as e:
        print(f"[X] Grok API Error: {e}")
        return False

def test_crawl4ai():
    """Test if Crawl4AI is installed"""
    print("\n" + "="*50)
    print("Testing Crawl4AI Installation")
    print("="*50)

    try:
        import crawl4ai
        print(f"[OK] Crawl4AI version {crawl4ai.__version__} is installed")
        return True
    except ImportError:
        print("[!] Crawl4AI is not installed yet")
        print("[!] Run: pip install -r requirements.txt")
        return False

def main():
    """Run all API tests"""
    print("\n" + "="*60)
    print("Reporter Database Updater - API Connection Tests")
    print("="*60)

    Config.print_config()

    results = {
        "Google Search": test_google_search(),
        "Grok API": test_grok_api(),
        "Crawl4AI": test_crawl4ai()
    }

    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)

    for name, success in results.items():
        status = "[OK]" if success else "[X]"
        print(f"{status} {name}")

    all_passed = all(results.values())

    if all_passed:
        print("\n[OK] All tests passed! Ready to build the prototype.")
    else:
        print("\n[!] Some tests failed. Please fix the issues above.")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
