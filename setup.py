#!/usr/bin/env python3
"""
Setup script for Daily Medium Writer Agent

This script helps with initial setup and configuration.
"""

import os
import sys
import subprocess
from pathlib import Path


def create_env_file():
    """Create .env file from template"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    env_content = """# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Medium API Configuration
MEDIUM_ACCESS_TOKEN=your_medium_access_token_here
MEDIUM_USER_ID=your_medium_user_id_here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/daily_medium_agent
REDIS_URL=redis://localhost:6379/0

# External APIs
NEWS_API_KEY=your_news_api_key_here
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
REDDIT_USER_AGENT=DailyMediumAgent/1.0

# Image Generation (Optional)
DALLE_API_KEY=your_dalle_api_key_here
UNSPLASH_ACCESS_KEY=your_unsplash_access_key_here

# Monitoring
SENTRY_DSN=your_sentry_dsn_here

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
MAX_ARTICLES_PER_DAY=1
HUMAN_REVIEW_REQUIRED=true
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file from template")
    print("⚠️  Please edit .env file with your actual API keys")


def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"Error output: {e.stderr}")
        return False
    return True


def create_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "static",
        "static/images",
        "templates",
        "data"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Created necessary directories")


def setup_database():
    """Setup database"""
    print("🗄️  Setting up database...")
    
    # Check if PostgreSQL is available
    try:
        subprocess.run(["psql", "--version"], check=True, capture_output=True)
        print("✅ PostgreSQL is available")
        
        # Try to create database
        db_name = "daily_medium_agent"
        try:
            subprocess.run(["createdb", db_name], check=True, capture_output=True)
            print(f"✅ Created database: {db_name}")
        except subprocess.CalledProcessError:
            print(f"⚠️  Database {db_name} might already exist")
            
    except subprocess.CalledProcessError:
        print("⚠️  PostgreSQL not found. Using SQLite as fallback.")
        # Update .env to use SQLite
        env_file = Path(".env")
        if env_file.exists():
            content = env_file.read_text()
            content = content.replace(
                "DATABASE_URL=postgresql://user:password@localhost:5432/daily_medium_agent",
                "DATABASE_URL=sqlite:///./data/daily_medium_agent.db"
            )
            env_file.write_text(content)
            print("✅ Updated .env to use SQLite")


def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 Setup completed!")
    print("="*60)
    print("\nNext steps:")
    print("1. Edit .env file with your API keys:")
    print("   - OpenAI API key (required)")
    print("   - Medium access token (required)")
    print("   - NewsAPI key (optional)")
    print("   - Reddit API credentials (optional)")
    print("   - Unsplash API key (optional)")
    print("\n2. Get Medium API credentials:")
    print("   - Go to https://medium.com/me/settings")
    print("   - Create an integration token")
    print("   - Get your user ID: curl -H 'Authorization: Bearer YOUR_TOKEN' https://api.medium.com/v1/me")
    print("\n3. Start the application:")
    print("   python run.py")
    print("\n4. Open your browser:")
    print("   http://localhost:8000")
    print("\n" + "="*60)


def main():
    """Main setup function"""
    print("🚀 Setting up Daily Medium Writer Agent...")
    print("="*50)
    
    steps = [
        ("Creating environment file", create_env_file),
        ("Installing dependencies", install_dependencies),
        ("Creating directories", create_directories),
        ("Setting up database", setup_database),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        try:
            result = step_func()
            if result is False:
                print(f"❌ {step_name} failed")
                sys.exit(1)
        except Exception as e:
            print(f"❌ {step_name} failed: {e}")
            sys.exit(1)
    
    print_next_steps()


if __name__ == "__main__":
    main()

