#!/usr/bin/env python3
"""
Test script to verify the Daily Medium Writer Agent setup
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    
    try:
        from config import settings
        print("✅ Config imported successfully")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from db.models import Article, Topic, ArticleStatus
        print("✅ Database models imported successfully")
    except Exception as e:
        print(f"❌ Database models import failed: {e}")
        return False
    
    try:
        from services.llm import LLMService
        print("✅ LLM service imported successfully")
    except Exception as e:
        print(f"❌ LLM service import failed: {e}")
        return False
    
    try:
        from services.medium import MediumService
        print("✅ Medium service imported successfully")
    except Exception as e:
        print(f"❌ Medium service import failed: {e}")
        return False
    
    try:
        from services.topics import TopicDiscoveryService
        print("✅ Topic discovery service imported successfully")
    except Exception as e:
        print(f"❌ Topic discovery service import failed: {e}")
        return False
    
    try:
        from services.images import ImageGenerationService
        print("✅ Image generation service imported successfully")
    except Exception as e:
        print(f"❌ Image generation service import failed: {e}")
        return False
    
    try:
        from services.safety import SafetyService
        print("✅ Safety service imported successfully")
    except Exception as e:
        print(f"❌ Safety service import failed: {e}")
        return False
    
    try:
        from services.scheduler import ArticleGenerationScheduler
        print("✅ Scheduler service imported successfully")
    except Exception as e:
        print(f"❌ Scheduler service import failed: {e}")
        return False
    
    return True


def test_configuration():
    """Test configuration"""
    print("\nTesting configuration...")
    
    try:
        from config import settings
        
        # Check required settings
        if not settings.openai_api_key:
            print("⚠️  OpenAI API key not configured")
        else:
            print("✅ OpenAI API key configured")
        
        if not settings.medium_access_token:
            print("⚠️  Medium access token not configured")
        else:
            print("✅ Medium access token configured")
        
        print(f"✅ Database URL: {settings.database_url}")
        print(f"✅ Debug mode: {settings.debug}")
        print(f"✅ Human review required: {settings.human_review_required}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_database():
    """Test database connection"""
    print("\nTesting database...")
    
    try:
        from db.database import engine, create_tables
        from sqlalchemy import text
        
        # Test connection
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        
        print("✅ Database connection successful")
        
        # Create tables
        create_tables()
        print("✅ Database tables created/verified")
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_services():
    """Test service initialization"""
    print("\nTesting services...")
    
    try:
        from services.llm import LLMService
        from services.medium import MediumService
        from services.topics import TopicDiscoveryService
        from services.images import ImageGenerationService
        from services.safety import SafetyService
        
        # Test service initialization
        llm_service = LLMService()
        print("✅ LLM service initialized")
        
        medium_service = MediumService()
        print("✅ Medium service initialized")
        
        topic_service = TopicDiscoveryService()
        print("✅ Topic discovery service initialized")
        
        image_service = ImageGenerationService()
        print("✅ Image generation service initialized")
        
        safety_service = SafetyService()
        print("✅ Safety service initialized")
        
        return True
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        return False


def test_fastapi():
    """Test FastAPI app"""
    print("\nTesting FastAPI app...")
    
    try:
        from main import app
        print("✅ FastAPI app imported successfully")
        
        # Test if app has expected routes
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/health", "/review", "/api/articles"]
        
        for route in expected_routes:
            if route in routes:
                print(f"✅ Route {route} found")
            else:
                print(f"⚠️  Route {route} not found")
        
        return True
    except Exception as e:
        print(f"❌ FastAPI test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Running Daily Medium Writer Agent setup tests...")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Database Test", test_database),
        ("Services Test", test_services),
        ("FastAPI Test", test_fastapi),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"🧪 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Configure your API keys in .env file")
        print("2. Run: python run.py")
        print("3. Open: http://localhost:8000")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

