from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging
import asyncio

from config import settings
from db.database import SessionLocal, engine, Base
from db.models import Email, Task, DailySummary, ProcessingLog, EmailStatus, TaskStatus
from services.scheduler import EmailProcessingScheduler
from services.gmail import GmailService
from services.tasks import GoogleTasksService
from services.email_processor import EmailProcessor
from services.safety import MonitoringService

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="Daily Email & Task Agent",
    description="AI-powered email processing and task automation",
    version="1.0.0"
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize services
scheduler = EmailProcessingScheduler()
gmail_service = GmailService()
tasks_service = GoogleTasksService()
email_processor = EmailProcessor()
monitoring_service = MonitoringService()

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    """Start the scheduler on application startup"""
    scheduler.start()
    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop the scheduler on application shutdown"""
    scheduler.stop()
    logger.info("Application shutdown complete")


# Web Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Main dashboard showing email and task overview"""
    
    # Get today's stats
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = today_start + timedelta(days=1)
    
    # Today's emails and tasks
    today_emails = db.query(Email).filter(
        Email.created_at >= today_start,
        Email.created_at < today_end
    ).count()
    
    today_tasks = db.query(Task).filter(
        Task.created_at >= today_start,
        Task.created_at < today_end
    ).count()
    
    # Pending tasks
    pending_tasks = db.query(Task).filter(
        Task.status == TaskStatus.PENDING
    ).order_by(desc(Task.created_at)).limit(5).all()
    
    # Recent emails
    recent_emails = db.query(Email).order_by(
        desc(Email.received_at)
    ).limit(10).all()
    
    # Today's summary
    today_summary = db.query(DailySummary).filter(
        DailySummary.date >= today_start,
        DailySummary.date < today_end
    ).first()
    
    # Stats
    total_emails = db.query(Email).count()
    processed_emails = db.query(Email).filter(
        Email.status == EmailStatus.PROCESSED
    ).count()
    total_tasks = db.query(Task).count()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "today_emails": today_emails,
        "today_tasks": today_tasks,
        "pending_tasks": pending_tasks,
        "recent_emails": recent_emails,
        "today_summary": today_summary,
        "total_emails": total_emails,
        "processed_emails": processed_emails,
        "total_tasks": total_tasks
    })


@app.get("/emails", response_class=HTMLResponse)
async def emails_page(request: Request, db: Session = Depends(get_db)):
    """Email processing page"""
    
    # Get emails with pagination
    emails = db.query(Email).order_by(desc(Email.received_at)).limit(50).all()
    
    # Stats
    total_emails = db.query(Email).count()
    processed_emails = db.query(Email).filter(
        Email.status == EmailStatus.PROCESSED
    ).count()
    unprocessed_emails = db.query(Email).filter(
        Email.status == EmailStatus.UNPROCESSED
    ).count()
    
    return templates.TemplateResponse("emails.html", {
        "request": request,
        "emails": emails,
        "total_emails": total_emails,
        "processed_emails": processed_emails,
        "unprocessed_emails": unprocessed_emails
    })


@app.get("/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request, db: Session = Depends(get_db)):
    """Task management page"""
    
    # Get tasks
    pending_tasks = db.query(Task).filter(
        Task.status == TaskStatus.PENDING
    ).order_by(desc(Task.created_at)).all()
    
    completed_tasks = db.query(Task).filter(
        Task.status == TaskStatus.COMPLETED
    ).order_by(desc(Task.completed_at)).limit(10).all()
    
    # Stats
    total_tasks = db.query(Task).count()
    high_priority_tasks = db.query(Task).filter(
        Task.priority.in_(["high", "urgent"]),
        Task.status == TaskStatus.PENDING
    ).count()
    
    return templates.TemplateResponse("tasks.html", {
        "request": request,
        "pending_tasks": pending_tasks,
        "completed_tasks": completed_tasks,
        "total_tasks": total_tasks,
        "high_priority_tasks": high_priority_tasks
    })


@app.get("/summaries", response_class=HTMLResponse)
async def summaries_page(request: Request, db: Session = Depends(get_db)):
    """Daily summaries page"""
    
    # Get recent summaries
    summaries = db.query(DailySummary).order_by(
        desc(DailySummary.date)
    ).limit(30).all()
    
    return templates.TemplateResponse("summaries.html", {
        "request": request,
        "summaries": summaries
    })


# API Routes
@app.post("/api/process-emails")
async def trigger_email_processing():
    """Manually trigger email processing"""
    try:
        job_id = scheduler.trigger_manual_processing()
        return {"message": "Email processing started", "job_id": job_id}
    except Exception as e:
        logger.error(f"Error triggering email processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sync-tasks")
async def sync_tasks():
    """Manually trigger task synchronization"""
    try:
        await scheduler.sync_google_tasks()
        return {"message": "Task synchronization completed"}
    except Exception as e:
        logger.error(f"Error syncing tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tasks")
async def create_task(
    title: str = Form(...),
    description: str = Form(""),
    due_date: Optional[str] = Form(None),
    priority: str = Form("medium"),
    db: Session = Depends(get_db)
):
    """Create a new task"""
    try:
        # Parse due date if provided
        parsed_due_date = None
        if due_date:
            parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        
        task = Task(
            title=title,
            description=description,
            due_date=parsed_due_date,
            priority=priority,
            extraction_method="manual"
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        return {"message": "Task created successfully", "task_id": task.id}
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tasks/{task_id}/complete")
async def complete_task(task_id: int, db: Session = Depends(get_db)):
    """Mark task as completed"""
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Task completed successfully"}
        
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/emails/{email_id}")
async def get_email(email_id: int, db: Session = Depends(get_db)):
    """Get email details"""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    return {
        "id": email.id,
        "sender": email.sender,
        "subject": email.subject,
        "body": email.body,
        "summary": email.summary,
        "importance_score": email.importance_score,
        "has_action_items": email.has_action_items,
        "status": email.status,
        "received_at": email.received_at
    }


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get application statistics"""
    
    # Basic counts
    total_emails = db.query(Email).count()
    processed_emails = db.query(Email).filter(
        Email.status == EmailStatus.PROCESSED
    ).count()
    total_tasks = db.query(Task).count()
    pending_tasks = db.query(Task).filter(
        Task.status == TaskStatus.PENDING
    ).count()
    
    # Cost and performance
    total_cost = db.query(func.sum(Email.processing_cost)).scalar() or 0.0
    total_tokens = db.query(func.sum(Email.tokens_used)).scalar() or 0
    
    # Recent activity (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    recent_emails = db.query(Email).filter(
        Email.created_at >= week_ago
    ).count()
    recent_tasks = db.query(Task).filter(
        Task.created_at >= week_ago
    ).count()
    
    return {
        "total_emails": total_emails,
        "processed_emails": processed_emails,
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "total_cost": total_cost,
        "total_tokens": total_tokens,
        "recent_emails": recent_emails,
        "recent_tasks": recent_tasks
    }


@app.get("/api/health")
async def health_check():
    """Application health check"""
    health = monitoring_service.check_system_health()
    return health


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)