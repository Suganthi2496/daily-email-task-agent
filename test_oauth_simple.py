#!/usr/bin/env python3
"""
Simple OAuth test to verify Google authentication works
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_oauth():
    """Test OAuth authentication with minimal setup"""
    print("🔐 Testing Google OAuth Authentication")
    print("=" * 45)
    
    # Check credentials file
    if not Path("credentials.json").exists():
        print("❌ credentials.json not found!")
        return False
    
    print("✅ Found credentials.json")
    
    # Set SQLite database to avoid PostgreSQL dependency
    os.environ['DATABASE_URL'] = 'sqlite:///./data/email_agent.db'
    
    try:
        print("🔄 Attempting Gmail authentication...")
        from services.gmail import GmailService
        
        # This will trigger the OAuth flow
        gmail_service = GmailService()
        print("✅ Gmail authentication successful!")
        
        # Test connection
        print("🔄 Testing Gmail API connection...")
        if gmail_service.test_connection():
            print("✅ Gmail API connection working!")
            return True
        else:
            print("❌ Gmail API connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you've added your email as a test user in Google Cloud Console")
        print("2. Go to: https://console.cloud.google.com/apis/credentials/consent")
        print("3. Add 'suganthi2496@gmail.com' to test users")
        print("4. Make sure Gmail API is enabled")
        return False

if __name__ == "__main__":
    if test_oauth():
        print("\n🎉 Google authentication is working!")
        print("You can now run: python test_google_apis.py")
    else:
        print("\n⚠️  Please fix the authentication issue first")
