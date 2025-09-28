# Daily Email & Task Automation Agent

An AI-powered system that automatically processes your emails, extracts actionable tasks, and syncs them with Google Tasks. Say goodbye to manual email processing and never miss an important task again!

## Features

- **Gmail Integration**: Automatically fetches and processes your emails
- **AI Email Analysis**: Smart summarization, importance scoring, and sentiment analysis
- **Task Extraction**: Automatically identifies and extracts actionable tasks from emails
- **Google Tasks Sync**: Creates and manages tasks directly in Google Tasks
- **Smart Dashboard**: Beautiful web interface to view emails, tasks, and daily summaries
- **Daily Summaries**: AI-generated daily reports of your email activity
- **Scheduling**: Fully automated daily processing with configurable timing
- **Cost Monitoring**: Tracks AI processing costs and token usage

## 🔐 Security & Confidential Files

**⚠️ IMPORTANT**: This project requires confidential files that should NEVER be committed to version control.

**Required confidential files:**
- `.env` - API keys and configuration
- `credentials.json` - Google OAuth credentials
- `token.json` - OAuth access tokens (auto-generated)

**📋 Setup Guide**: See [SETUP_CONFIDENTIAL_FILES.md](SETUP_CONFIDENTIAL_FILES.md) for detailed instructions on setting up these files securely.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gmail API     │    │   AI Email      │    │   Google Tasks  │
│   Email Fetch   │───▶│   Processing    │───▶│   Integration   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Email         │    │   OpenAI GPT    │    │   Web Dashboard │
│   Database      │    │   Analysis      │    │   Interface     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd daily-email-task-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Google API Setup

```bash
# Run the Google setup guide
python configure_google.py
```

Follow the guide to:
1. Create a Google Cloud project
2. Enable Gmail and Google Tasks APIs
3. Create OAuth credentials
4. Download `credentials.json`

### 3. Configuration

```bash
# Run the configuration script
python configure_env.py
```

This will ask for your API keys:
- **OpenAI API Key** (required) - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- Google credentials (already set up in step 2)

### 4. Test Setup

```bash
# Test Google APIs
python test_google_apis.py

# Test overall setup
python test_setup.py
```

### 5. Run the Application

```bash
# Start the application
python run.py
```

Visit `http://localhost:8000` to access the dashboard.

## Usage

### How It Works

1. **Morning Processing** (8 AM daily, configurable):
   - Fetches unread emails from Gmail
   - Analyzes each email with AI for importance and sentiment
   - Generates concise summaries
   - Extracts actionable tasks automatically
   - Syncs tasks to Google Tasks

2. **Dashboard Access**:
   - View email summaries and importance scores
   - See extracted tasks with due dates and priorities
   - Read AI-generated daily summaries
   - Monitor processing costs and performance

3. **Manual Processing**:
   - Click "Process Emails" to run immediately
   - Click "Sync Tasks" to update Google Tasks

### API Endpoints

- `GET /` - Main dashboard
- `GET /emails` - Email processing view
- `GET /tasks` - Task management view
- `GET /summaries` - Daily summaries view
- `POST /api/process-emails` - Trigger email processing
- `POST /api/sync-tasks` - Sync with Google Tasks
- `GET /api/emails` - List emails with filtering
- `GET /api/tasks` - List tasks with filtering
- `GET /health` - System health check

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `GOOGLE_CREDENTIALS_FILE` | Path to Google credentials JSON | `credentials.json` |
| `GOOGLE_TOKEN_FILE` | Path to Google OAuth token | `token.json` |
| `DATABASE_URL` | Database connection string | SQLite |
| `GMAIL_MAX_EMAILS` | Max emails to fetch per run | `50` |
| `PROCESS_UNREAD_ONLY` | Only process unread emails | `true` |
| `EMAIL_PROCESSING_SCHEDULE` | Daily processing time | `8:00` |
| `MAX_DAILY_PROCESSING` | Max emails per day | `100` |
| `DEBUG` | Debug mode | `true` |

### Scheduling

Modify `services/scheduler.py` to change:
- Email processing time (default: 8 AM daily)
- Google Tasks sync frequency (default: every 4 hours)
- Health check frequency (default: hourly)
- Data cleanup schedule (default: weekly)

### Email Processing Customization

Edit configuration to customize:
- Which emails to process (unread, starred, etc.)
- AI analysis parameters
- Task extraction confidence thresholds

## Safety & Privacy

### Email Privacy

- All email processing happens locally on your machine
- No emails are sent to external services except OpenAI for analysis
- OpenAI processes email content but doesn't store it
- You maintain full control of your email data

### Content Moderation

- Basic content filtering for inappropriate content
- Task extraction confidence scoring
- Quality checks for task relevance
- Cost monitoring and usage alerts

### Rate Limiting

- Configurable daily email processing limits
- API rate limiting for OpenAI calls
- Google API quota monitoring
- Processing cost tracking

## Monitoring & Analytics

### Performance Metrics

- Email processing time and costs
- Task extraction accuracy
- API usage and token consumption
- Success/failure rates for each operation

### Daily Reports

- AI-generated summaries of email activity
- Task completion statistics
- Important email highlights
- Cost and performance analytics

### Health Checks

- Gmail and Google Tasks API connectivity
- OpenAI API availability
- Database connectivity
- System resource usage
- Processing queue status

### Logging

- Comprehensive operation logging
- Error tracking and alerting
- Performance metrics collection
- Cost tracking per operation

## Deployment

### Production Setup

1. **Database**: Use PostgreSQL instead of SQLite
2. **Environment**: Set `DEBUG=false`
3. **Monitoring**: Configure Sentry DSN
4. **Reverse Proxy**: Use Nginx for static files
5. **Process Manager**: Use systemd or supervisor
6. **SSL**: Configure HTTPS with Let's Encrypt

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment-Specific Configs

- **Development**: SQLite, debug mode, manual triggers
- **Staging**: PostgreSQL, review required, limited publishing
- **Production**: Full automation, monitoring, backups

## Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   - Check API key validity
   - Monitor rate limits and quotas
   - Verify model availability

2. **Medium Publishing Fails**
   - Validate integration token
   - Check user permissions
   - Verify content format

3. **Topic Discovery Issues**
   - Confirm external API keys
   - Check network connectivity
   - Review rate limiting

4. **Database Connection**
   - Verify DATABASE_URL format
   - Check database server status
   - Ensure proper permissions

### Logs and Debugging

```bash
# View application logs
tail -f logs/app.log

# Check scheduler status
curl http://localhost:8000/health

# Monitor database
psql daily_medium_agent -c "SELECT * FROM articles ORDER BY created_at DESC LIMIT 5;"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review logs for error details
- Open an issue on GitHub
- Check API documentation for external services

## Roadmap

- [ ] Multi-platform publishing (LinkedIn, Twitter)
- [ ] Advanced analytics and A/B testing
- [ ] Custom writing style training
- [ ] Collaborative review workflow
- [ ] SEO optimization recommendations
- [ ] Content calendar planning

