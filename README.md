# IT Support Technical Assistant 🛠️

An AI-powered IT support system that helps you solve everyday technology problems through intelligent reasoning and a user-friendly chat interface.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![React](https://img.shields.io/badge/React-18.2-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 Quick Start (2 Minutes)

1. **Get an OpenAI API Key**: [Get it here](https://platform.openai.com/api-keys) (required)

2. **First Time Setup**:

   ```powershell
   .\setup-simple.ps1
   ```

   - Installs Python and Node.js packages
   - Creates configuration files
   - Opens `.env` file to add your API key

3. **Run the Application**:

   ```powershell
   .\run.ps1
   ```

4. **Open Browser**: Go to http://localhost:3000

5. **Try Asking**:
   - "My Wi-Fi won't connect"
   - "Computer is very slow"
   - "Printer not printing"

That's it! 🎉

## 🌟 Features

- **Intelligent Problem Diagnosis**: Breaks down complex IT issues step-by-step
- **Knowledge Base**: Powered by vector database with IT support documentation
- **Natural Language**: Understands vague queries and asks clarifying questions
- **Step-by-Step Solutions**: Clear troubleshooting steps with risk assessments
- **Safety Warnings**: Alerts you before risky actions
- **Conversation Memory**: Tracks attempted solutions

### Supported Problems

- 🌐 Networking (Wi-Fi, connectivity)
- ⚡ Performance (slow computers, freezing)
- 💻 OS issues (Windows, macOS, Linux)
- 🖨️ Peripherals (printers, keyboards, monitors)
- 📱 Mobile devices (battery, storage, apps)
- 🔧 Hardware (power, overheating)

## 💡 How to Use

Once running, just type your problem in plain English:

- "My Wi-Fi keeps disconnecting"
- "Computer is slow and freezing"
- "Printer says offline but it's plugged in"
- "Phone battery drains too fast"

The AI will ask clarifying questions if needed, then provide step-by-step solutions.

## 🔧 Advanced Setup (Optional)

### Add More Knowledge

Populate the knowledge base with IT documentation:

```powershell
cd backend
python -m data.data_collection
python -m data.preprocessing
python -m data.embeddings
```

### Run Tests

```powershell
cd backend
pytest tests/ -v
```

## ⚙️ Configuration

Edit `backend\.env` to customize:

```bash
# LLM Configuration
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
DEFAULT_LLM_PROVIDER=openai  # or anthropic
DEFAULT_MODEL=gpt-3.5-turbo

# Vector Database
CHROMA_PERSIST_DIRECTORY=./data/chroma_db
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.7

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
RATE_LIMIT_PER_MINUTE=30

# Safety
ENABLE_SAFETY_CHECKS=True
```

#### Frontend (.env)

```bash
VITE_API_URL=http://localhost:8000/api
```

## 📁 Project Structure

```
AI Project/
├── backend/
│   ├── api/
│   │   ├── main.py              # FastAPI application
│   │   ├── routes.py            # API endpoints
│   │   ├── models.py            # Pydantic models
│   │   └── config.py            # Configuration
│   ├── services/
│   │   ├── rag_service.py       # RAG retrieval
│   │   ├── llm_service.py       # LLM integration
│   │   ├── reasoning_engine.py  # Multi-step reasoning
│   │   └── safety_checker.py    # Safety validation
│   ├── data/
│   │   ├── data_collection.py   # Data scraping
│   │   ├── preprocessing.py     # Data cleaning
│   │   └── embeddings.py        # Vector generation
│   ├── tests/
│   │   ├── test_api.py
│   │   ├── test_rag.py
│   │   └── test_reasoning.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWindow.jsx
│   │   │   ├── Message.jsx
│   │   │   ├── SolutionSteps.jsx
│   │   │   └── DeviceInfoForm.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🎯 API Endpoints

### Main Endpoints

#### POST /api/chat

Send a chat message for IT support.

```json
{
  "message": "My Wi-Fi won't connect",
  "session_id": "optional-session-id",
  "device_info": {
    "device_type": "laptop",
    "os": "windows",
    "os_version": "11"
  },
  "technical_level": "beginner"
}
```

#### POST /api/analyze

Analyze a problem without full solution.

```json
{
  "problem_description": "Computer is very slow",
  "device_info": {
    "device_type": "desktop",
    "os": "windows"
  }
}
```

#### POST /api/solutions/search

Search knowledge base for solutions.

```json
{
  "query": "printer not printing",
  "problem_category": "peripherals",
  "limit": 10
}
```

#### POST /api/feedback

Submit feedback on a solution.

```json
{
  "session_id": "session-id",
  "rating": "helpful",
  "solved": true,
  "comment": "Great help!"
}
```

## 🔒 Security Features

- **Input Validation**: Pydantic models validate all requests
- **Rate Limiting**: Prevents API abuse
- **Safety Checks**: Warns before risky operations
- **CORS Protection**: Configurable allowed origins
- **Content Security**: XSS and injection prevention

## 🎨 User Interface Features

- **Dark/Light Mode**: Automatic theme switching
- **Mobile Responsive**: Works on all devices
- **Step Progress Tracking**: Visual checkboxes for solution steps
- **Real-time Chat**: Smooth message streaming
- **Device Info Management**: Store device details for better help
- **Feedback System**: Rate solutions and provide comments
- **Copy Commands**: Easy command copying for terminal actions

## 📈 Performance Metrics

Target Performance:

- **Response Time**: < 3 seconds
- **Retrieval Accuracy**: > 85%
- **Solution Success Rate**: > 70%
- **System Uptime**: 99.5%

## 🛠️ Troubleshooting

### Backend Issues

**ChromaDB Connection Error**

```powershell
# Delete and reinitialize the database
Remove-Item -Recurse -Force backend/data/chroma_db
python -m data.embeddings
```

**LLM API Errors**

- Verify API keys in `.env`
- Check API quota and billing
- System works in fallback mode without API keys

### Frontend Issues

**Cannot Connect to API**

- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify proxy configuration in `vite.config.js`

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) - Interactive Swagger UI
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Development Guide](docs/DEVELOPMENT.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ChromaDB** - Vector database
- **Sentence Transformers** - Embedding models
- **FastAPI** - Backend framework
- **React** - Frontend library
- **OpenAI/Anthropic** - LLM providers

## 📧 Support

For support, email support@itsupport-ai.com or open an issue on GitHub.

## 🗺️ Roadmap

- [ ] Voice input support
- [ ] Multi-language support
- [ ] Screenshot analysis
- [ ] Remote desktop integration
- [ ] Mobile apps (iOS/Android)
- [ ] Advanced analytics dashboard
- [ ] Custom knowledge base training

---

**Made with ❤️ for better IT support**
