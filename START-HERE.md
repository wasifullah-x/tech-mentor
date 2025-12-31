## ⚡ Super Quick Start

**First time?**

1. Get OpenAI API key: https://platform.openai.com/api-keys
2. Run: `.\setup-simple.ps1` (installs everything, opens .env to add key)
3. Run: `.\run.ps1` (starts frontend + backend)
4. Open: http://localhost:3000

**Already set up?**
Just run: `.\run.ps1`

That's it! Ask the AI your tech problems.

## 💬 Try These Questions

- "My Wi-Fi keeps disconnecting"
- "Computer is very slow and freezing"
- "Printer says offline but it's connected"
- "Phone battery drains in 2 hours"
- "Blue screen error when I boot up"
- "Can't connect Bluetooth headphones"

## 🛑 To Stop

Close both PowerShell windows that opened (backend + frontend)

## ⚠️ Common Issues

**"Module not found" errors**: Run `.\setup-simple.ps1` again

**"API key invalid"**: Edit `backend\.env` and add real OpenAI key

**"Port already in use"**: Close other apps using ports 3000 or 8000

**"Backend won't start"**: Check `backend\logs\app.log` for details

## 📁 What's Inside

- `backend/` - FastAPI server with AI logic
- `frontend/` - React chat interface
- `run.ps1` - Starts everything
- `setup-simple.ps1` - First time setup

Need more details? See [README.md](README.md)
