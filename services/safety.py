import logging
import re
from typing import Dict, Any, List, Optional
from openai import OpenAI
from config import settings
import requests
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class SafetyService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.blocked_patterns = [
            r'\b(fake news|conspiracy|hoax)\b',
            r'\b(hate speech|racist|sexist)\b',
            r'\b(illegal|piracy|crack)\b',
        ]
        
    def moderate_content(self, content: str, title: str = "") -> Dict[str, Any]:
        """
        Comprehensive content moderation
        
        Returns:
            Dictionary with moderation results and recommendations
        """
        results = {
            "safe": True,
            "issues": [],
            "warnings": [],
            "recommendations": [],
            "confidence": 1.0
        }
        
        # OpenAI Moderation API
        openai_result = self._openai_moderation(content)
        if not openai_result["safe"]:
            results["safe"] = False
            results["issues"].extend(openai_result["issues"])
        
        # Custom pattern matching
        pattern_result = self._pattern_moderation(content, title)
        if not pattern_result["safe"]:
            results["safe"] = False
            results["issues"].extend(pattern_result["issues"])
        
        # Content quality checks
        quality_result = self._quality_checks(content, title)
        results["warnings"].extend(quality_result["warnings"])
        results["recommendations"].extend(quality_result["recommendations"])
        
        # Plagiarism check (basic)
        plagiarism_result = self._basic_plagiarism_check(content)
        if plagiarism_result["warnings"]:
            results["warnings"].extend(plagiarism_result["warnings"])
        
        # Calculate overall confidence
        results["confidence"] = self._calculate_confidence(results)
        
        return results
    
    def _openai_moderation(self, content: str) -> Dict[str, Any]:
        """Use OpenAI's moderation API"""
        try:
            response = self.openai_client.moderations.create(input=content)
            
            moderation = response.results[0]
            
            if moderation.flagged:
                issues = []
                categories = moderation.categories
                
                if categories.hate:
                    issues.append("Hate speech detected")
                if categories.harassment:
                    issues.append("Harassment content detected")
                if categories.self_harm:
                    issues.append("Self-harm content detected")
                if categories.sexual:
                    issues.append("Sexual content detected")
                if categories.violence:
                    issues.append("Violence content detected")
                
                return {"safe": False, "issues": issues}
            
            return {"safe": True, "issues": []}
        
        except Exception as e:
            logger.error(f"OpenAI moderation error: {e}")
            return {"safe": True, "issues": []}  # Fail open for availability
    
    def _pattern_moderation(self, content: str, title: str) -> Dict[str, Any]:
        """Custom pattern-based moderation"""
        issues = []
        full_text = f"{title} {content}".lower()
        
        for pattern in self.blocked_patterns:
            if re.search(pattern, full_text, re.IGNORECASE):
                issues.append(f"Potentially problematic content detected: {pattern}")
        
        # Check for excessive capitalization (shouting)
        if len(re.findall(r'[A-Z]{5,}', content)) > 3:
            issues.append("Excessive capitalization detected")
        
        # Check for spam patterns
        if len(re.findall(r'(click here|buy now|limited time)', content, re.IGNORECASE)) > 2:
            issues.append("Potential spam patterns detected")
        
        return {"safe": len(issues) == 0, "issues": issues}
    
    def _quality_checks(self, content: str, title: str) -> Dict[str, Any]:
        """Content quality checks"""
        warnings = []
        recommendations = []
        
        # Length checks
        word_count = len(content.split())
        if word_count < 300:
            warnings.append("Article is quite short (under 300 words)")
            recommendations.append("Consider expanding the content for better engagement")
        elif word_count > 3000:
            warnings.append("Article is quite long (over 3000 words)")
            recommendations.append("Consider breaking into multiple parts or sections")
        
        # Title checks
        if len(title) > 100:
            warnings.append("Title is very long (over 100 characters)")
            recommendations.append("Consider shortening the title for better readability")
        elif len(title) < 30:
            warnings.append("Title is quite short (under 30 characters)")
            recommendations.append("Consider making the title more descriptive")
        
        # Readability checks
        sentences = content.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        if avg_sentence_length > 25:
            warnings.append("Average sentence length is high")
            recommendations.append("Consider breaking up long sentences for better readability")
        
        # Check for proper structure
        if '<h2>' not in content and '<h3>' not in content:
            warnings.append("No subheadings detected")
            recommendations.append("Add subheadings to improve article structure")
        
        # Check for links and references
        if 'http' not in content and 'www.' not in content:
            warnings.append("No external links or references found")
            recommendations.append("Consider adding relevant links to support your points")
        
        return {"warnings": warnings, "recommendations": recommendations}
    
    def _basic_plagiarism_check(self, content: str) -> Dict[str, Any]:
        """Basic plagiarism detection using text patterns"""
        warnings = []
        
        # Check for common copied phrases (this is very basic)
        common_phrases = [
            "according to wikipedia",
            "as stated in the documentation",
            "copy and paste",
            "lorem ipsum"
        ]
        
        content_lower = content.lower()
        for phrase in common_phrases:
            if phrase in content_lower:
                warnings.append(f"Potentially copied phrase detected: '{phrase}'")
        
        # Check for unusual quotation patterns
        quote_count = content.count('"')
        if quote_count > 20:
            warnings.append("High number of quotations - verify all sources are properly attributed")
        
        return {"warnings": warnings}
    
    def _calculate_confidence(self, results: Dict[str, Any]) -> float:
        """Calculate confidence score for moderation results"""
        base_confidence = 1.0
        
        # Reduce confidence for each issue
        base_confidence -= len(results["issues"]) * 0.2
        
        # Reduce confidence for warnings
        base_confidence -= len(results["warnings"]) * 0.05
        
        return max(0.0, min(1.0, base_confidence))
    
    def check_rate_limits(self, user_id: str = "default") -> Dict[str, Any]:
        """Check if user/system is within rate limits"""
        # This is a simple implementation - in production, use Redis or similar
        from db.database import SessionLocal
        from db.models import Article
        from datetime import datetime, timedelta
        
        db = SessionLocal()
        try:
            # Check articles published in last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_articles = db.query(Article).filter(
                Article.created_at >= yesterday,
                Article.status == "published"
            ).count()
            
            max_daily = settings.max_articles_per_day
            
            return {
                "within_limits": recent_articles < max_daily,
                "current_count": recent_articles,
                "max_allowed": max_daily,
                "reset_time": (datetime.utcnow() + timedelta(days=1)).isoformat()
            }
        
        finally:
            db.close()
    
    def log_safety_event(self, event_type: str, content_id: Optional[int], 
                        details: Dict[str, Any]) -> None:
        """Log safety-related events"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "content_id": content_id,
            "details": details
        }
        
        # Log to file (in production, use proper logging infrastructure)
        logger.warning(f"Safety event: {json.dumps(log_entry)}")
        
        # In production, also send to monitoring service like Sentry
        if settings.sentry_dsn:
            try:
                import sentry_sdk
                sentry_sdk.capture_message(
                    f"Safety event: {event_type}",
                    level="warning",
                    extra=log_entry
                )
            except ImportError:
                pass


class ContentValidator:
    """Additional content validation utilities"""
    
    @staticmethod
    def validate_html_content(content: str) -> Dict[str, Any]:
        """Validate HTML content structure"""
        issues = []
        recommendations = []
        
        # Check for basic HTML structure
        if '<p>' not in content:
            issues.append("No paragraph tags found")
        
        # Check for proper heading hierarchy
        h1_count = content.count('<h1>')
        if h1_count > 1:
            issues.append("Multiple H1 tags found - should only have one")
        
        # Check for alt text in images
        img_tags = re.findall(r'<img[^>]*>', content)
        for img in img_tags:
            if 'alt=' not in img:
                recommendations.append("Add alt text to images for accessibility")
        
        # Check for proper link structure
        link_tags = re.findall(r'<a[^>]*>', content)
        for link in link_tags:
            if 'href=' not in link:
                issues.append("Link tag without href attribute found")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "recommendations": recommendations
        }
    
    @staticmethod
    def validate_medium_requirements(article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate article meets Medium's requirements"""
        issues = []
        warnings = []
        
        # Title requirements
        title = article_data.get("title", "")
        if len(title) > 100:
            warnings.append("Title may be too long for optimal Medium display")
        
        # Tags requirements
        tags = article_data.get("tags", [])
        if len(tags) > 5:
            issues.append("Medium allows maximum 5 tags")
        
        # Content length
        content = article_data.get("content", "")
        word_count = len(content.split())
        if word_count < 150:
            warnings.append("Very short articles may not perform well on Medium")
        
        # Image requirements
        if not article_data.get("featured_image_url"):
            warnings.append("Featured image recommended for better engagement")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }


class MonitoringService:
    """Service for monitoring system health and performance"""
    
    def __init__(self):
        self.metrics = {}
    
    def record_generation_metrics(self, step: str, duration: float, 
                                 tokens_used: int, cost: float) -> None:
        """Record metrics for content generation steps"""
        if step not in self.metrics:
            self.metrics[step] = {
                "count": 0,
                "total_duration": 0,
                "total_tokens": 0,
                "total_cost": 0
            }
        
        self.metrics[step]["count"] += 1
        self.metrics[step]["total_duration"] += duration
        self.metrics[step]["total_tokens"] += tokens_used
        self.metrics[step]["total_cost"] += cost
        
        # Log metrics
        logger.info(f"Metrics - {step}: {duration:.2f}s, {tokens_used} tokens, ${cost:.4f}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        summary = {}
        
        for step, data in self.metrics.items():
            if data["count"] > 0:
                summary[step] = {
                    "average_duration": data["total_duration"] / data["count"],
                    "average_tokens": data["total_tokens"] / data["count"],
                    "average_cost": data["total_cost"] / data["count"],
                    "total_executions": data["count"]
                }
        
        return summary
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        health = {
            "status": "healthy",
            "checks": {}
        }
        
        # Check database connection
        try:
            from db.database import SessionLocal
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            health["checks"]["database"] = "ok"
        except Exception as e:
            health["checks"]["database"] = f"error: {str(e)}"
            health["status"] = "unhealthy"
        
        # Check OpenAI API
        try:
            client = OpenAI(api_key=settings.openai_api_key)
            client.models.list()
            health["checks"]["openai"] = "ok"
        except Exception as e:
            health["checks"]["openai"] = f"error: {str(e)}"
            health["status"] = "degraded"
        
        # Check Medium API
        try:
            from services.medium import MediumService
            medium = MediumService()
            if medium.validate_connection():
                health["checks"]["medium"] = "ok"
            else:
                health["checks"]["medium"] = "connection failed"
                health["status"] = "degraded"
        except Exception as e:
            health["checks"]["medium"] = f"error: {str(e)}"
            health["status"] = "degraded"
        
        return health

