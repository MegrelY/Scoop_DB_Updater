"""
Configuration management for Reporter Database Updater
Loads environment variables and provides configuration access
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Application configuration loaded from environment variables"""

    # API Keys
    GROK_API_KEY = os.getenv('GROK_API_KEY')
    GROK_BASE_URL = os.getenv('GROK_BASE_URL', 'https://api.x.ai/v1')
    GROK_MODEL = os.getenv('GROK_MODEL', 'grok-beta')

    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GOOGLE_SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

    # Project Settings
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 50))
    CONFIDENCE_THRESHOLD = int(os.getenv('CONFIDENCE_THRESHOLD', 70))
    OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'output')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DB_SAMPLE_PATH = PROJECT_ROOT / 'DB-Sample' / 'Sample list.csv'
    OUTPUT_PATH = PROJECT_ROOT / OUTPUT_FOLDER
    LOGS_PATH = PROJECT_ROOT / 'logs'
    CACHE_PATH = PROJECT_ROOT / 'cache'

    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        errors = []

        if not cls.GROK_API_KEY:
            errors.append("GROK_API_KEY is not set in .env file")

        if not cls.GOOGLE_API_KEY:
            errors.append("GOOGLE_API_KEY is not set in .env file (will set up next)")

        if not cls.GOOGLE_SEARCH_ENGINE_ID:
            errors.append("GOOGLE_SEARCH_ENGINE_ID is not set in .env file (will set up next)")

        return errors

    @classmethod
    def print_config(cls):
        """Print configuration (hiding sensitive values)"""
        print("=" * 50)
        print("Reporter Database Updater - Configuration")
        print("=" * 50)
        print(f"Grok API Key: {'[OK] Set' if cls.GROK_API_KEY else '[X] Missing'}")
        print(f"Grok Model: {cls.GROK_MODEL}")
        print(f"Google API Key: {'[OK] Set' if cls.GOOGLE_API_KEY else '[X] Missing'}")
        print(f"Batch Size: {cls.BATCH_SIZE}")
        print(f"Confidence Threshold: {cls.CONFIDENCE_THRESHOLD}%")
        print(f"Project Root: {cls.PROJECT_ROOT}")
        print(f"DB Sample: {cls.DB_SAMPLE_PATH}")
        print("=" * 50)

if __name__ == "__main__":
    # Test configuration loading
    Config.print_config()
    errors = Config.validate()
    if errors:
        print("\n[!] Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n[OK] Configuration is valid!")
