# 🚀 Git Deployment Guide

This guide explains how to safely deploy the Daily Email & Task Agent to a Git repository.

## 🔐 Security Checklist

Before pushing to Git, ensure:

### ✅ Confidential Files Protected
- [ ] `.gitignore` updated with all confidential files
- [ ] No API keys or secrets in committed code
- [ ] Template files created for confidential files
- [ ] Security check script passes

### ✅ Run Security Check
```bash
python check_git_security.py
```
This script verifies that confidential files are properly ignored.

## 📁 Files Safe to Commit

### ✅ Source Code
- All `.py` files
- `requirements.txt`
- `setup.py`
- Configuration templates

### ✅ Documentation
- `README.md`
- `SETUP_CONFIDENTIAL_FILES.md`
- `GIT_DEPLOYMENT_GUIDE.md`
- `PROJECT_STRUCTURE.md`

### ✅ Templates & Examples
- `.env.example`
- `credentials.json.example`
- `check_git_security.py`

### ✅ Web Interface
- `templates/` directory (HTML files)
- `static/` directory (CSS, JS, images)

## 🚫 Files NEVER to Commit

### ❌ Confidential Files
- `.env` - Contains API keys
- `credentials.json` - Google OAuth credentials
- `token.json` - OAuth access tokens
- `*.backup` files

### ❌ Data Files
- `data/email_agent.db` - Personal email data
- `logs/*.log` - Application logs
- `*.csv` files with personal data

### ❌ System Files
- `venv/` - Virtual environment
- `__pycache__/` - Python cache
- `.DS_Store` - macOS system files

## 🔧 Git Setup Commands

### Initialize Repository
```bash
# Initialize git repository
git init

# Add all safe files
git add .

# Check what will be committed
git status

# Run security check
python check_git_security.py

# Commit initial version
git commit -m "Initial commit: Daily Email & Task Agent"
```

### Connect to Remote Repository
```bash
# Add remote repository
git remote add origin https://github.com/yourusername/daily-email-task-agent.git

# Push to remote
git push -u origin main
```

## 🔄 Deployment to New Environment

When deploying to a new environment:

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/daily-email-task-agent.git
cd daily-email-task-agent
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Confidential Files
```bash
# Copy templates
cp .env.example .env
cp credentials.json.example credentials.json

# Edit with actual values
nano .env
nano credentials.json
```

### 4. Set Up Database
```bash
python -c "from db.database import create_tables; create_tables()"
```

### 5. Run Application
```bash
uvicorn main:app --host 0.0.0.0 --port 8002
```

## 🛡️ Security Best Practices

### Repository Settings
- Make repository **private** if it contains any sensitive logic
- Enable branch protection rules
- Require pull request reviews
- Enable security alerts

### Environment Variables
- Use environment variables for all secrets
- Never hardcode API keys in source code
- Use different API keys for development/production

### Access Control
- Limit repository access to necessary team members
- Use deploy keys for automated deployments
- Regularly audit repository access

## 🔍 Regular Security Maintenance

### Monthly Checks
- [ ] Run `python check_git_security.py`
- [ ] Review git history for accidentally committed secrets
- [ ] Update dependencies in `requirements.txt`
- [ ] Rotate API keys if needed

### Before Each Commit
- [ ] Run security check script
- [ ] Review `git status` output
- [ ] Ensure no confidential files are staged

## 🆘 Emergency: Secrets Accidentally Committed

If you accidentally commit confidential files:

### 1. Immediate Actions
```bash
# Remove from staging
git reset HEAD <filename>

# Remove from working directory if needed
git checkout -- <filename>
```

### 2. If Already Pushed
```bash
# Remove from history (DANGEROUS - rewrites history)
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch <filename>' \
--prune-empty --tag-name-filter cat -- --all

# Force push (only if repository is private and you're sure)
git push origin --force --all
```

### 3. Rotate Compromised Secrets
- Generate new API keys immediately
- Update all environments with new keys
- Revoke old keys

## 📞 Support

For deployment issues:
1. Check the security guide: `SETUP_CONFIDENTIAL_FILES.md`
2. Run the security check: `python check_git_security.py`
3. Review the main README.md for setup instructions

---

**⚠️ Remember**: Security is paramount. When in doubt, don't commit. It's easier to add files later than to remove secrets from git history.
