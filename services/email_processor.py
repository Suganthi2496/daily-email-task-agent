import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from config import settings
from db.models import Email, EmailStatus, Task, TaskStatus, ProcessingLog
from db.database import SessionLocal
from services.tasks import GoogleTasksService
import logging
import re

logger = logging.getLogger(__name__)


class EmailProcessor:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.langchain_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            openai_api_key=settings.openai_api_key
        )
        self.tasks_service = GoogleTasksService()
        
    def process_email(self, email: Email) -> Dict[str, Any]:
        """
        Process a single email through the complete AI pipeline
        
        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        total_tokens = 0
        total_cost = 0.0
        
        try:
            logger.info(f"Processing email: {email.subject[:50]}...")
            
            # Step 1: Analyze email importance and sentiment
            importance_result = self._analyze_importance(email)
            if importance_result is None:
                # API quota exceeded - skip AI processing
                logger.info(f"Skipping AI processing for email {email.id} due to API quota limits")
                return {
                    'success': False,
                    'email_id': email.id,
                    'error': 'OpenAI API quota exceeded',
                    'processing_time': time.time() - start_time
                }
            total_tokens += importance_result.get('tokens_used', 0)
            total_cost += importance_result.get('cost', 0)
            
            # Step 2: Generate summary
            summary_result = self._generate_summary(email)
            if summary_result is None:
                # Use fallback summary
                summary_result = {
                    'summary': f"Email from {email.sender}: {email.subject}",
                    'tokens_used': 0,
                    'cost': 0.0
                }
            total_tokens += summary_result.get('tokens_used', 0)
            total_cost += summary_result.get('cost', 0)
            
            # Step 3: Extract action items/tasks
            tasks_result = self._extract_tasks(email)
            if tasks_result is None:
                # Use fallback empty tasks
                tasks_result = {
                    'tasks': [],
                    'tokens_used': 0,
                    'cost': 0.0
                }
            total_tokens += tasks_result.get('tokens_used', 0)
            total_cost += tasks_result.get('cost', 0)
            
            # Step 4: Update email record
            self._update_email_record(
                email, 
                importance_result, 
                summary_result, 
                tasks_result,
                total_tokens,
                total_cost
            )
            
            # Step 5: Create tasks in Google Tasks
            created_tasks = []
            if tasks_result.get('tasks'):
                for task_data in tasks_result['tasks']:
                    task_id = self._create_task_from_email(email, task_data)
                    if task_id:
                        created_tasks.append(task_id)
            
            processing_time = time.time() - start_time
            
            # Log successful processing
            self._log_processing(
                'email_process',
                'success',
                f"Processed email: {email.subject[:50]}",
                {
                    'email_id': email.id,
                    'importance_score': importance_result.get('importance_score', 0),
                    'tasks_extracted': len(created_tasks),
                    'summary_length': len(summary_result.get('summary', ''))
                },
                processing_time,
                total_tokens,
                total_cost
            )
            
            return {
                'success': True,
                'email_id': email.id,
                'importance_score': importance_result.get('importance_score', 0),
                'summary': summary_result.get('summary', ''),
                'sentiment': importance_result.get('sentiment', 'neutral'),
                'tasks_created': created_tasks,
                'processing_time': processing_time,
                'tokens_used': total_tokens,
                'cost': total_cost
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error processing email {email.id}: {e}")
            
            # Log error
            self._log_processing(
                'email_process',
                'error',
                f"Failed to process email: {str(e)}",
                {'email_id': email.id},
                processing_time,
                total_tokens,
                total_cost
            )
            
            return {
                'success': False,
                'email_id': email.id,
                'error': str(e),
                'processing_time': processing_time
            }
    
    def _analyze_importance(self, email: Email) -> Dict[str, Any]:
        """Analyze email importance and sentiment"""
        prompt = f"""
        Analyze this email for importance and sentiment:
        
        From: {email.sender}
        Subject: {email.subject}
        Body: {email.body[:1000]}...
        
        Return a JSON response with:
        1. importance_score: float (0.0 to 1.0, where 1.0 is most important)
        2. sentiment: string ("positive", "negative", "neutral", "urgent")
        3. reasoning: string (brief explanation)
        4. is_actionable: boolean (contains action items)
        
        Consider these factors for importance:
        - Sender (boss, client, important contacts = higher importance)
        - Subject urgency keywords (urgent, deadline, ASAP, etc.)
        - Content that requires action
        - Meeting requests, deadlines, client communications
        
        JSON format only:
        """
        
        try:
            messages = [
                {"role": "system", "content": "You are an expert email analyst. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3,
                max_tokens=300
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                **result,
                'tokens_used': response.usage.total_tokens,
                'cost': response.usage.total_tokens * 0.00003  # Approximate cost
            }
            
        except Exception as e:
            logger.error(f"Error analyzing importance: {e}")
            # Check if it's a quota exceeded error
            if "insufficient_quota" in str(e) or "429" in str(e):
                logger.warning("OpenAI API quota exceeded - skipping AI analysis")
                return None  # Signal to skip AI processing
            return {
                'importance_score': 0.5,
                'sentiment': 'neutral',
                'reasoning': 'Analysis failed',
                'is_actionable': False,
                'tokens_used': 0,
                'cost': 0.0
            }
    
    def _generate_summary(self, email: Email) -> Dict[str, Any]:
        """Generate concise email summary"""
        prompt = f"""
        Summarize this email in 2-3 clear, actionable sentences:
        
        From: {email.sender}
        Subject: {email.subject}
        Body: {email.body[:2000]}...
        
        Requirements:
        - Focus on key information and any actions needed
        - Use professional, clear language
        - Highlight deadlines or important dates
        - Keep it under 150 words
        
        Summary:
        """
        
        try:
            messages = [
                {"role": "system", "content": "You are an expert at creating concise, actionable email summaries."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3,
                max_tokens=200
            )
            
            summary = response.choices[0].message.content.strip()
            
            return {
                'summary': summary,
                'tokens_used': response.usage.total_tokens,
                'cost': response.usage.total_tokens * 0.00003
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            # Check if it's a quota exceeded error
            if "insufficient_quota" in str(e) or "429" in str(e):
                logger.warning("OpenAI API quota exceeded - using fallback summary")
                return None  # Signal to skip AI processing
            return {
                'summary': f"Email from {email.sender}: {email.subject}",
                'tokens_used': 0,
                'cost': 0.0
            }
    
    def _extract_tasks(self, email: Email) -> Dict[str, Any]:
        """Extract actionable tasks from email"""
        prompt = f"""
        Extract actionable tasks from this email:
        
        From: {email.sender}
        Subject: {email.subject}
        Body: {email.body[:2000]}...
        
        Return a JSON response with an array of tasks. For each task include:
        - title: string (concise task description)
        - description: string (more details if needed)
        - due_date: string (ISO format date if mentioned, null if not)
        - priority: string ("low", "medium", "high", "urgent")
        - confidence: float (0.0 to 1.0 - how confident you are this is a real task)
        
        Only extract tasks that are:
        - Clearly actionable (not just FYI)
        - Directed at the email recipient
        - Specific enough to be acted upon
        
        If no clear tasks, return empty array.
        
        JSON format:
        {{"tasks": [...]}}
        """
        
        try:
            messages = [
                {"role": "system", "content": "You are an expert at extracting actionable tasks from emails. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.2,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Parse and validate due dates
            for task in result.get('tasks', []):
                if task.get('due_date'):
                    try:
                        task['due_date'] = self._parse_due_date(task['due_date'])
                    except:
                        task['due_date'] = None
            
            return {
                **result,
                'tokens_used': response.usage.total_tokens,
                'cost': response.usage.total_tokens * 0.00003
            }
            
        except Exception as e:
            logger.error(f"Error extracting tasks: {e}")
            # Check if it's a quota exceeded error
            if "insufficient_quota" in str(e) or "429" in str(e):
                logger.warning("OpenAI API quota exceeded - skipping task extraction")
                return None  # Signal to skip AI processing
            return {
                'tasks': [],
                'tokens_used': 0,
                'cost': 0.0
            }
    
    def _parse_due_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats into datetime"""
        if not date_str:
            return None
            
        # Common date patterns
        patterns = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%m/%d/%Y",
            "%d/%m/%Y"
        ]
        
        for pattern in patterns:
            try:
                return datetime.strptime(date_str, pattern)
            except ValueError:
                continue
        
        # Try relative dates
        date_str_lower = date_str.lower()
        today = datetime.now().replace(hour=17, minute=0, second=0, microsecond=0)  # Default to 5 PM
        
        if 'today' in date_str_lower:
            return today
        elif 'tomorrow' in date_str_lower:
            return today + timedelta(days=1)
        elif 'monday' in date_str_lower:
            days_ahead = 0 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return today + timedelta(days=days_ahead)
        elif 'friday' in date_str_lower:
            days_ahead = 4 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return today + timedelta(days=days_ahead)
        elif 'next week' in date_str_lower:
            return today + timedelta(days=7)
        
        return None
    
    def _update_email_record(self, email: Email, importance_result: Dict, 
                           summary_result: Dict, tasks_result: Dict,
                           total_tokens: int, total_cost: float):
        """Update email record with processing results"""
        db = SessionLocal()
        try:
            email.summary = summary_result.get('summary', '')
            email.importance_score = importance_result.get('importance_score', 0.0)
            email.sentiment = importance_result.get('sentiment', 'neutral')
            email.has_action_items = len(tasks_result.get('tasks', [])) > 0
            email.tokens_used = total_tokens
            email.processing_cost = total_cost
            email.status = EmailStatus.PROCESSED
            email.processed_at = datetime.utcnow()
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating email record: {e}")
        finally:
            db.close()
    
    def _create_task_from_email(self, email: Email, task_data: Dict) -> Optional[int]:
        """Create a task in the database and Google Tasks"""
        try:
            # Only create tasks with reasonable confidence
            if task_data.get('confidence', 0) < 0.6:
                logger.info(f"Skipping low-confidence task: {task_data.get('title')}")
                return None
            
            task_id = self.tasks_service.save_task_to_db(
                title=task_data['title'],
                description=task_data.get('description', ''),
                due_date=task_data.get('due_date'),
                priority=task_data.get('priority', 'medium'),
                email_id=email.id,
                confidence_score=task_data.get('confidence', 0.0)
            )
            
            if task_id:
                logger.info(f"Created task: {task_data['title']}")
            
            return task_id
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None
    
    def _log_processing(self, operation: str, status: str, message: str, 
                       details: Dict, duration: float, tokens: int, cost: float):
        """Log processing operation"""
        db = SessionLocal()
        try:
            log = ProcessingLog(
                operation=operation,
                status=status,
                message=message,
                details=details,
                duration_seconds=duration,
                tokens_used=tokens,
                cost=cost
            )
            db.add(log)
            db.commit()
        except Exception as e:
            logger.error(f"Error logging operation: {e}")
        finally:
            db.close()
    
    def process_unprocessed_emails(self) -> Dict[str, Any]:
        """Process all unprocessed emails"""
        db = SessionLocal()
        try:
            unprocessed_emails = db.query(Email).filter(
                Email.status == EmailStatus.UNPROCESSED
            ).order_by(Email.received_at.desc()).all()
            
            if not unprocessed_emails:
                logger.info("No unprocessed emails found")
                return {'processed': 0, 'errors': 0, 'total_cost': 0.0}
            
            logger.info(f"Processing {len(unprocessed_emails)} unprocessed emails")
            
            results = {
                'processed': 0,
                'errors': 0,
                'total_cost': 0.0,
                'total_tokens': 0,
                'tasks_created': 0
            }
            
            for email in unprocessed_emails:
                result = self.process_email(email)
                
                if result['success']:
                    results['processed'] += 1
                    results['total_cost'] += result.get('cost', 0)
                    results['total_tokens'] += result.get('tokens_used', 0)
                    results['tasks_created'] += len(result.get('tasks_created', []))
                else:
                    results['errors'] += 1
                
                # Small delay to avoid rate limiting
                time.sleep(1)
            
            logger.info(f"Processing complete: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error processing emails: {e}")
            return {'processed': 0, 'errors': 1, 'total_cost': 0.0}
        finally:
            db.close()
    
    def generate_daily_summary(self, date: datetime = None) -> Dict[str, Any]:
        """Generate AI summary of the day's emails and tasks"""
        if not date:
            date = datetime.now()
        
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        db = SessionLocal()
        try:
            # Get today's processed emails
            emails = db.query(Email).filter(
                Email.processed_at >= start_date,
                Email.processed_at < end_date,
                Email.status == EmailStatus.PROCESSED
            ).all()
            
            # Get today's tasks
            tasks = db.query(Task).filter(
                Task.created_at >= start_date,
                Task.created_at < end_date
            ).all()
            
            if not emails and not tasks:
                return {
                    'summary': "No emails or tasks processed today.",
                    'stats': {
                        'emails_processed': 0,
                        'tasks_created': 0,
                        'high_priority_tasks': 0
                    }
                }
            
            # Generate summary using AI
            summary_prompt = self._build_daily_summary_prompt(emails, tasks)
            summary = self._generate_ai_summary(summary_prompt)
            
            # Calculate statistics
            stats = {
                'emails_processed': len(emails),
                'important_emails': len([e for e in emails if e.importance_score > 0.7]),
                'tasks_created': len(tasks),
                'high_priority_tasks': len([t for t in tasks if t.priority in ['high', 'urgent']]),
                'total_cost': sum(e.processing_cost or 0 for e in emails),
                'avg_importance': sum(e.importance_score or 0 for e in emails) / len(emails) if emails else 0
            }
            
            return {
                'summary': summary,
                'stats': stats,
                'date': date.strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
            return {
                'summary': f"Error generating summary: {str(e)}",
                'stats': {},
                'date': date.strftime('%Y-%m-%d')
            }
        finally:
            db.close()
    
    def _build_daily_summary_prompt(self, emails: List[Email], tasks: List[Task]) -> str:
        """Build prompt for daily summary generation"""
        email_summaries = []
        for email in emails[:10]:  # Limit to top 10 emails
            email_summaries.append(f"• From {email.sender}: {email.summary}")
        
        task_summaries = []
        for task in tasks:
            due_str = f" (due {task.due_date.strftime('%Y-%m-%d')})" if task.due_date else ""
            task_summaries.append(f"• {task.title}{due_str} [{task.priority} priority]")
        
        prompt = f"""
        Create a concise daily summary for today's email processing:
        
        EMAILS PROCESSED ({len(emails)} total):
        {chr(10).join(email_summaries)}
        
        TASKS EXTRACTED ({len(tasks)} total):
        {chr(10).join(task_summaries)}
        
        Create a 3-4 sentence summary highlighting:
        1. Key themes from today's emails
        2. Most important tasks extracted
        3. Any urgent items requiring immediate attention
        4. Overall productivity insights
        
        Keep it professional and actionable.
        """
        
        return prompt
    
    def _generate_ai_summary(self, prompt: str) -> str:
        """Generate AI summary from prompt"""
        try:
            messages = [
                {"role": "system", "content": "You are an executive assistant providing daily email and task summaries."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            return "Unable to generate AI summary at this time."
