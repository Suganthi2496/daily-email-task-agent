# Daily Email & Task Agent - Complete Project Index

## 📋 Project Overview

**Daily Email & Task Agent** is an AI-powered automation system that processes Gmail emails, extracts actionable tasks, and syncs them with Google Tasks. It provides a modern web interface for managing emails, tasks, and daily summaries.

### 🎯 Core Functionality
- **Gmail Integration**: Fetches and processes emails automatically
- **AI Analysis**: Uses OpenAI GPT models for email summarization and task extraction
- **Task Management**: Creates and syncs tasks with Google Tasks
- **Web Dashboard**: Modern FastAPI-based web interface
- **Automated Scheduling**: Daily processing with configurable timing
- **Monitoring & Analytics**: Comprehensive logging and health checks

---

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gmail API     │    │   AI Email      │    │   Google Tasks  │
│   Email Fetch   │───▶│   Processing    │───▶│   Integration   │
│                 │    │   (OpenAI GPT)  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SQLite        │    │   FastAPI       │    │   Web Dashboard │
│   Database      │    │   Web Server    │    │   Interface     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 📁 Project Structure

### Root Files
- **`main.py`** - FastAPI web application with all endpoints
- **`config.py`** - Pydantic settings management with environment variables
- **`requirements.txt`** - Python dependencies (26 packages)
- **`run.py`** - Application launcher with dependency checks
- **`setup.py`** - Initial setup helper script

### Setup & Configuration Scripts
- **`configure_env.py`** - Interactive environment configuration
- **`configure_google.py`** - Google APIs setup guide
- **`test_google_apis.py`** - Test Google API connections
- **`test_setup.py`** - Complete system test
- **`test_oauth_simple.py`** - Simple OAuth authentication test

### Database Layer (`db/`)
- **`database.py`** - SQLAlchemy database connection and session management
- **`models.py`** - Database models (Email, Task, DailySummary, ProcessingLog)

### Core Services (`services/`)
- **`gmail.py`** - Gmail API integration with OAuth authentication
- **`email_processor.py`** - AI-powered email analysis and processing
- **`tasks.py`** - Google Tasks API integration and task management
- **`scheduler.py`** - Automated daily processing with APScheduler
- **`safety.py`** - Monitoring, health checks, and safety features
- **`llm.py`** - LLM service abstraction
- **`topics.py`** - Topic discovery service
- **`file_export.py`** - File export utilities

### Web Interface (`templates/`)
- **`base.html`** - Base template with navigation and styling
- **`dashboard.html`** - Main dashboard with today's stats
- **`emails.html`** - Email processing and management view
- **`tasks.html`** - Task management and completion view
- **`summaries.html`** - Daily summaries and analytics
- **`404.html`** & **`500.html`** - Error pages

### Data Storage
- **`data/`** - SQLite database storage
- **`logs/`** - Application logs
- **`static/images/`** - Generated images storage

---

## 🔧 Core Services Detailed

### 1. Gmail Service (`services/gmail.py`)
**Purpose**: Gmail API integration and email fetching

**Key Features**:
- OAuth 2.0 authentication with Google
- Fetches emails with configurable filters (unread, starred)
- Extracts email content from various MIME types
- Retry logic with exponential backoff
- Rate limiting to prevent API abuse
- Database integration for email storage

**Main Methods**:
- `get_recent_emails()` - Fetch emails from Gmail
- `save_emails_to_db()` - Store emails in local database
- `test_connection()` - Verify API connectivity
- `_authenticate()` - Handle OAuth flow

### 2. Email Processor (`services/email_processor.py`)
**Purpose**: AI-powered email analysis and task extraction

**Key Features**:
- OpenAI GPT-4o-mini integration for analysis
- Email importance scoring (0-1 scale)
- Sentiment analysis (positive/negative/neutral/urgent)
- Automatic task extraction with confidence scoring
- Cost tracking for AI API usage
- Comprehensive error handling

**Processing Pipeline**:
1. **Importance Analysis** - Scores email importance
2. **Summary Generation** - Creates concise summaries
3. **Task Extraction** - Identifies actionable items
4. **Database Update** - Stores analysis results
5. **Task Creation** - Creates tasks in Google Tasks

**Main Methods**:
- `process_email()` - Complete email processing pipeline
- `process_unprocessed_emails()` - Batch processing
- `generate_daily_summary()` - AI-generated daily reports

### 3. Google Tasks Service (`services/tasks.py`)
**Purpose**: Google Tasks API integration and task management

**Key Features**:
- OAuth 2.0 authentication (shared with Gmail)
- Task creation, updating, and completion
- Sync with Google Tasks cloud service
- Local database storage for offline access
- Retry logic for network resilience
- Task list management

**Main Methods**:
- `create_task()` - Create new tasks
- `get_tasks()` - Retrieve tasks from Google
- `sync_with_google_tasks()` - Bidirectional sync
- `save_task_to_db()` - Local database storage

### 4. Scheduler Service (`services/scheduler.py`)
**Purpose**: Automated daily processing and task scheduling

**Key Features**:
- APScheduler for background job management
- Configurable daily email processing (default: 8 AM)
- Google Tasks sync every 6 hours
- System health checks every 2 hours
- Daily summary generation (6 PM)
- Weekly data cleanup

**Scheduled Jobs**:
- **Daily Email Processing** - Fetch and process new emails
- **Google Tasks Sync** - Sync tasks with cloud
- **Health Checks** - Monitor system status
- **Daily Summaries** - Generate AI reports
- **Data Cleanup** - Remove old logs and data

### 5. Safety & Monitoring (`services/safety.py`)
**Purpose**: System monitoring, health checks, and safety features

**Key Features**:
- Database connectivity monitoring
- OpenAI API health checks
- Cost tracking and usage monitoring
- Error logging and alerting
- Performance metrics collection

---

## 🗄️ Database Schema

### Email Table
- **Primary Data**: Gmail ID, sender, subject, body, received date
- **Processing**: Status, processed timestamp, AI analysis results
- **AI Analysis**: Summary, importance score, sentiment, action items
- **Costs**: Tokens used, processing cost

### Task Table
- **Content**: Title, description, due date, priority
- **Status**: Pending/completed/cancelled, completion timestamp
- **Integration**: Google Task ID, task list ID
- **AI Metadata**: Confidence score, extraction method
- **Relationships**: Links to source email

### Daily Summary Table
- **Statistics**: Email counts, task counts, processing metrics
- **AI Content**: Generated summary text, key topics, top senders
- **Performance**: Processing time, token usage, costs

### Processing Log Table
- **Operations**: Email fetch, processing, task creation
- **Status**: Success/error/warning with detailed messages
- **Performance**: Duration, token usage, costs
- **Debugging**: Structured details in JSON format

---

## 🌐 Web Interface & API

### Web Pages
1. **Dashboard** (`/`) - Today's stats, recent activity, quick actions
2. **Emails** (`/emails`) - Email list, processing status, summaries
3. **Tasks** (`/tasks`) - Task management, completion tracking
4. **Summaries** (`/summaries`) - Historical daily reports

### API Endpoints
- **`GET /health`** - System health status
- **`POST /api/process-emails`** - Trigger manual email processing
- **`POST /api/sync-tasks`** - Manual Google Tasks sync
- **`GET /api/emails`** - List emails with filtering
- **`GET /api/tasks`** - List tasks with filtering
- **`POST /api/tasks`** - Create new tasks
- **`GET /api/stats`** - System statistics

### Frontend Technology
- **Framework**: FastAPI with Jinja2 templates
- **Styling**: Tailwind CSS for modern UI
- **Icons**: Font Awesome for consistent iconography
- **Responsive**: Mobile-friendly design

---

## ⚙️ Configuration

### Environment Variables (`.env`)
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Google APIs
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json

# Database
DATABASE_URL=sqlite:///./data/email_agent.db

# Email Processing
GMAIL_MAX_EMAILS=50
PROCESS_UNREAD_ONLY=true
EMAIL_PROCESSING_SCHEDULE=8:00

# Application
DEBUG=true
LOG_LEVEL=INFO
MAX_DAILY_PROCESSING=100
```

### Key Settings
- **Email Processing**: Configurable filters, limits, and scheduling
- **AI Models**: OpenAI GPT-4o-mini for cost-effective processing
- **Task Management**: Default task list name and priorities
- **Monitoring**: Health check intervals and logging levels

---

## 🚀 Deployment & Operations

### Development Setup
1. **Environment**: Python 3.9+ with virtual environment
2. **Dependencies**: Install via `pip install -r requirements.txt`
3. **Google APIs**: Configure OAuth credentials
4. **OpenAI**: Set up API key with billing
5. **Database**: SQLite for local development

### Production Considerations
- **Database**: Upgrade to PostgreSQL for production
- **Monitoring**: Configure Sentry for error tracking
- **Scaling**: Use Redis for task queuing
- **Security**: Environment variable management
- **Backup**: Regular database backups

### Current Status
- ✅ **Gmail API**: Working with retry logic
- ✅ **Google Tasks API**: Working with sync capabilities
- ✅ **Web Interface**: Running on port 8002
- ✅ **Database**: SQLite with all tables created
- ⚠️ **OpenAI API**: Requires active billing/credits
- ✅ **Scheduler**: Automated processing active

---

## 📊 Performance & Monitoring

### Metrics Tracked
- **Processing Time**: Email analysis duration
- **API Costs**: OpenAI token usage and costs
- **Success Rates**: Processing success/failure ratios
- **Task Accuracy**: AI task extraction confidence
- **System Health**: Database, API connectivity

### Logging
- **Application Logs**: Comprehensive operation logging
- **Error Tracking**: Detailed error messages and stack traces
- **Performance Logs**: Processing times and resource usage
- **Cost Tracking**: Per-operation cost analysis

---

## 🔐 Security & Privacy

### Data Privacy
- **Local Processing**: All email data processed locally
- **User Control**: Complete control over email data
- **No External Storage**: Emails not stored by third parties
- **Secure APIs**: OAuth 2.0 for Google services

### Security Features
- **OAuth Authentication**: Secure Google API access
- **Token Management**: Automatic token refresh
- **Error Handling**: Graceful failure handling
- **Rate Limiting**: API abuse prevention

---

## 📈 Future Enhancements

### Planned Features
- **Multi-account Support**: Handle multiple Gmail accounts
- **Advanced Filtering**: Custom email processing rules
- **Mobile App**: React Native mobile interface
- **Integrations**: Slack, Microsoft Teams, Notion
- **Analytics**: Advanced reporting and insights

### Technical Improvements
- **Caching**: Redis for improved performance
- **Microservices**: Service decomposition for scaling
- **Testing**: Comprehensive test suite
- **CI/CD**: Automated deployment pipeline
- **Documentation**: API documentation with OpenAPI

---

This project represents a complete, production-ready email automation system with modern architecture, comprehensive features, and robust error handling. The codebase is well-structured, documented, and ready for both personal use and further development.
