#!/usr/bin/env python3
"""
Interactive script to configure your .env file with API keys
"""

import os
from pathlib import Path

def create_env_file():
    """Create .env file with user input"""
    env_file = Path(".env")
    
    print("🔧 Daily Medium Writer Agent Configuration")
    print("=" * 50)
    print("This script will help you configure your API keys.")
    print("Press Enter to skip optional keys.\n")
    
    # Required keys
    print("📋 REQUIRED API KEYS:")
    print("-" * 20)
    
    openai_key = input("OpenAI API Key (sk-...): ").strip()
    if not openai_key:
        print("❌ OpenAI API key is required!")
        return False
    
    medium_token = input("Medium Access Token: ").strip()
    if not medium_token:
        print("❌ Medium access token is required!")
        return False
    
    # Get Medium User ID
    print("\n🔍 Getting your Medium User ID...")
    print("We'll use your access token to fetch your user ID automatically.")
    
    try:
        import requests
        headers = {
            "Authorization": f"Bearer {medium_token}",
            "Content-Type": "application/json"
        }
        response = requests.get("https://api.medium.com/v1/me", headers=headers)
        response.raise_for_status()
        
        user_data = response.json().get("data", {})
        medium_user_id = user_data.get('id')
        
        if medium_user_id:
            print(f"✅ Found your Medium User ID: {medium_user_id}")
            print(f"   Username: {user_data.get('username')}")
            print(f"   Name: {user_data.get('name')}")
        else:
            print("❌ Could not get user ID from Medium API")
            medium_user_id = input("Please enter your Medium User ID manually: ").strip()
    
    except Exception as e:
        print(f"❌ Error connecting to Medium API: {e}")
        medium_user_id = input("Please enter your Medium User ID manually: ").strip()
    
    if not medium_user_id:
        print("❌ Medium User ID is required!")
        return False
    
    # Optional keys
    print("\n📋 OPTIONAL API KEYS (press Enter to skip):")
    print("-" * 40)
    
    news_api_key = input("NewsAPI Key (for topic discovery): ").strip()
    reddit_client_id = input("Reddit Client ID: ").strip()
    reddit_client_secret = input("Reddit Client Secret: ").strip()
    unsplash_key = input("Unsplash Access Key (for images): ").strip()
    
    # Create .env content
    env_content = f"""# OpenAI Configuration
OPENAI_API_KEY={openai_key}

# Medium API Configuration
MEDIUM_ACCESS_TOKEN={medium_token}
MEDIUM_USER_ID={medium_user_id}

# Database Configuration
DATABASE_URL=sqlite:///./data/daily_medium_agent.db
REDIS_URL=redis://localhost:6379/0

# External APIs (Optional)
NEWS_API_KEY={news_api_key}
REDDIT_CLIENT_ID={reddit_client_id}
REDDIT_CLIENT_SECRET={reddit_client_secret}
REDDIT_USER_AGENT=DailyMediumAgent/1.0

# Image Generation (Optional)
UNSPLASH_ACCESS_KEY={unsplash_key}

# Monitoring (Optional)
SENTRY_DSN=

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
MAX_ARTICLES_PER_DAY=1
HUMAN_REVIEW_REQUIRED=true
"""
    
    # Write .env file
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"\n✅ Configuration saved to {env_file}")
        print("\n🎉 Setup complete! Your API keys are configured.")
        
        # Show next steps
        print("\n📋 NEXT STEPS:")
        print("1. Install dependencies: source venv/bin/activate && pip install -r requirements.txt")
        print("2. Test setup: python test_setup.py")
        print("3. Start application: python run.py")
        print("4. Open browser: http://localhost:8000")
        
        return True
        
    except Exception as e:
        print(f"❌ Error writing .env file: {e}")
        return False

def main():
    """Main configuration function"""
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    if create_env_file():
        print("\n🚀 Ready to start your Daily Medium Writer Agent!")
    else:
        print("\n❌ Configuration failed. Please try again.")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

