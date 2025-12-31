# 🚀 Quick Start Guide

Get the IT Support Assistant running in 5 minutes!

## Prerequisites Check

- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed
- ✅ OpenAI or Anthropic API key ready

## Installation (Windows)

### Step 1: Get API Key

**Option A - OpenAI (Recommended):**

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

**Option B - Anthropic:**

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key

### Step 2: Run Setup Script

Open PowerShell in the project directory:

```powershell
# Run automated setup
.\setup.ps1
```

This will:

- ✅ Check Python and Node.js
- ✅ Install all dependencies
- ✅ Create virtual environment
- ✅ Set up directories
- ✅ Create .env file

**When prompted:** Edit `backend\.env` and add your API key:

```bash
OPENAI_API_KEY=sk-your-key-here
```

### Step 3: Start the Application

```powershell
.\start.ps1
```

### Step 4: Open Your Browser

Go to: **http://localhost:3000**

That's it! 🎉

## First Use

1. **Set Device Info** (optional): Click the "Set Device Info" button to tell the assistant about your device
2. **Ask a Question**: Type something like "My Wi-Fi won't connect"
3. **Follow Solutions**: Check off steps as you complete them
4. **Give Feedback**: Rate solutions to help improve the system

## Example Questions to Try

- "My computer is running very slow"
- "Printer won't print"
- "Laptop won't turn on"
- "Phone battery draining fast"
- "Can't connect to Wi-Fi"
- "Blue screen error on Windows"

## Manual Start (Alternative)

If the automated script doesn't work:

**Terminal 1 - Backend:**

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn api.main:app --reload
```

**Terminal 2 - Frontend:**

```powershell
cd frontend
npm run dev
```

## Troubleshooting

### "Python not found"

Install from: https://www.python.org/downloads/

### "Node.js not found"

Install from: https://nodejs.org/

### "Cannot connect to API"

1. Check backend is running on port 8000
2. Check `.env` file has valid API key
3. Try restarting both backend and frontend

### "LLM API Error"

- Verify API key in `backend\.env`
- Check your OpenAI/Anthropic account has credits
- System works in limited mode without API key

## What's Next?

- 📖 Read [README.md](README.md) for full features
- 🔧 Check [DEVELOPMENT.md](DEVELOPMENT.md) for customization
- 🚀 See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment

## Need Help?

- Check logs in `backend/logs/app.log`
- API docs at http://localhost:8000/docs
- Open an issue on GitHub

---

**Enjoy your AI IT Support Assistant!** 🛠️✨
