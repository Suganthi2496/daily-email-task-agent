# 🔐 Confidential Files Setup Guide

This guide explains how to set up the confidential files required for the Daily Email & Task Agent.

## 📋 Required Confidential Files

### 1. `.env` - Environment Variables
**Template**: `.env.example`
**Purpose**: Contains API keys and configuration settings

**Setup Steps:**
1. Copy `.env.example` to `.env`
2. Fill in your actual values:
   - `OPENAI_API_KEY`: Get from https://platform.openai.com/api-keys
   - Other settings can use the default values

### 2. `credentials.json` - Google API Credentials
**Template**: `credentials.json.example`
**Purpose**: Google OAuth client credentials for Gmail and Tasks APIs

**Setup Steps:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API and Google Tasks API
4. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
5. Choose "Desktop application"
6. Download the JSON file and rename it to `credentials.json`
7. Place it in the project root directory

### 3. `token.json` - Google OAuth Token
**Auto-generated**: This file is created automatically during first authentication
**Purpose**: Stores OAuth access and refresh tokens

**Setup Steps:**
- This file is created automatically when you first run the application
- You'll be prompted to authenticate via browser
- The token is saved for future use

## 🚨 Security Notes

### Files That Should NEVER be Committed:
- `.env` - Contains API keys
- `credentials.json` - Contains OAuth client secrets
- `token.json` - Contains access tokens
- `data/email_agent.db` - Contains personal email data
- Any `.backup` files

### Files Safe to Commit:
- `.env.example` - Template without real values
- `credentials.json.example` - Template without real credentials
- All Python source code files
- Configuration templates
- Documentation files

## 🔧 Quick Setup Commands

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit with your values
nano .env  # or use your preferred editor

# 3. Add your Google credentials
# Download from Google Cloud Console and save as credentials.json

# 4. Run the application (will prompt for OAuth)
python main.py
```

## 🔍 Verification

Check that confidential files are properly ignored:
```bash
# This should show no confidential files
git status

# This should list the ignored files
git ls-files --others --ignored --exclude-standard
```

## 📚 Getting API Keys

### OpenAI API Key
1. Visit https://platform.openai.com/
2. Sign in or create account
3. Go to API Keys section
4. Create new secret key
5. Add billing information and credits
6. Copy key to `.env` file

### Google API Setup
1. Visit https://console.cloud.google.com/
2. Create new project or select existing
3. Enable APIs:
   - Gmail API
   - Google Tasks API
4. Create OAuth 2.0 credentials
5. Download credentials file
6. Add your email as test user in OAuth consent screen

## 🆘 Troubleshooting

### Common Issues:
1. **"No module named" errors**: Install requirements with `pip install -r requirements.txt`
2. **OAuth errors**: Ensure you're added as test user in Google Cloud Console
3. **API quota exceeded**: Add credits to OpenAI account
4. **Permission denied**: Check file permissions and paths

### Getting Help:
- Check the main README.md for detailed setup instructions
- Review error logs in the `logs/` directory
- Ensure all confidential files are properly configured

## 🔄 Updating Credentials

### To Update OpenAI API Key:
1. Edit `.env` file
2. Update `OPENAI_API_KEY` value
3. Restart application

### To Update Google Credentials:
1. Delete `token.json` file
2. Replace `credentials.json` with new file
3. Restart application (will re-authenticate)

---

**⚠️ Important**: Never commit confidential files to version control. Always use the template files and setup instructions for new deployments.
