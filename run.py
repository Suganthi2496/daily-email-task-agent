#!/usr/bin/env python3
"""
Daily Medium Writer Agent - Startup Script

This script provides a convenient way to start the application with proper
initialization and error handling.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import settings


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/app.log') if os.path.exists('logs') else logging.NullHandler()
        ]
    )


def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'openai', 'requests',
        'praw', 'feedparser', 'apscheduler', 'pillow'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True


def check_configuration():
    """Check if required configuration is present"""
    required_configs = ['openai_api_key']
    recommended_configs = ['medium_access_token', 'medium_user_id']
    
    missing_required = []
    missing_recommended = []
    
    for config in required_configs:
        if not getattr(settings, config, None):
            missing_required.append(config.upper())
    
    for config in recommended_configs:
        if not getattr(settings, config, None):
            missing_recommended.append(config.upper())
    
    if missing_required:
        print(f"❌ Missing required configuration: {', '.join(missing_required)}")
        print("Please set these in your .env file")
        return False
    
    if missing_recommended:
        print(f"⚠️  Missing recommended configuration: {', '.join(missing_recommended)}")
        print("The application will work but with limited functionality")
    
    print("✅ Configuration check passed")
    return True


def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'static', 'static/images', 'templates']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Directories created/verified")


def test_database_connection():
    """Test database connection"""
    try:
        from db.database import engine
        from sqlalchemy import text
        
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please check your DATABASE_URL configuration")
        return False


def test_external_apis():
    """Test external API connections"""
    from services.safety import SafetyService
    from services.medium import MediumService
    
    # Test OpenAI
    try:
        safety_service = SafetyService()
        result = safety_service._openai_moderation("test content")
        print("✅ OpenAI API connection successful")
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        return False
    
    # Test Medium API (if configured)
    if settings.medium_access_token:
        try:
            medium_service = MediumService()
            if medium_service.validate_connection():
                print("✅ Medium API connection successful")
            else:
                print("⚠️  Medium API connection failed - check your token")
        except Exception as e:
            print(f"⚠️  Medium API test failed: {e}")
    
    return True


def initialize_database():
    """Initialize database tables"""
    try:
        from db.database import create_tables
        create_tables()
        print("✅ Database tables initialized")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def main():
    """Main startup function"""
    print("🚀 Starting Daily Medium Writer Agent...")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Pre-flight checks
    checks = [
        ("Dependencies", check_dependencies),
        ("Configuration", check_configuration),
        ("Directories", lambda: (create_directories(), True)[1]),
        ("Database Connection", test_database_connection),
        ("Database Initialization", initialize_database),
        ("External APIs", test_external_apis),
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        try:
            if not check_func():
                failed_checks.append(check_name)
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
            failed_checks.append(check_name)
    
    if failed_checks:
        print(f"\n❌ Startup failed. Failed checks: {', '.join(failed_checks)}")
        print("\nPlease fix the issues above and try again.")
        sys.exit(1)
    
    print("\n✅ All checks passed! Starting the application...")
    print("=" * 50)
    
    # Start the application
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=settings.debug,
            log_level=settings.log_level.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

