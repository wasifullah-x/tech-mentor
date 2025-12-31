# Development Guide

## Prerequisites

### System Requirements

- **OS**: Windows 10/11, macOS, or Linux
- **Python**: 3.11 or higher
- **Node.js**: 18 or higher
- **RAM**: 8GB minimum (16GB recommended)
- **Disk Space**: 5GB for dependencies and data

### Required Accounts

- **OpenAI Account**: For GPT models (https://platform.openai.com)
  - OR **Anthropic Account**: For Claude models (https://console.anthropic.com)

## Development Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd "AI Project"
```

### 2. Backend Setup

```powershell
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and add your API keys
```

### 3. Frontend Setup

```powershell
cd frontend

# Install dependencies
npm install

# Create environment file (if needed)
cp .env.example .env
```

### 4. Initialize Knowledge Base

```powershell
cd backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run data collection (optional - sample data is auto-loaded)
python -m data.data_collection

# Preprocess data
python -m data.preprocessing

# Generate embeddings
python -m data.embeddings
```

## Running in Development Mode

### Option 1: Automated Start (Windows)

```powershell
# Run setup (first time only)
.\setup.ps1

# Start application
.\start.ps1
```

### Option 2: Manual Start

**Terminal 1 - Backend:**

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**

```powershell
cd frontend
npm run dev
```

## Project Structure Explained

```
AI Project/
├── backend/
│   ├── api/                    # FastAPI application
│   │   ├── main.py            # App initialization, lifespan
│   │   ├── routes.py          # Endpoint definitions
│   │   ├── models.py          # Pydantic schemas
│   │   └── config.py          # Settings management
│   │
│   ├── services/              # Core business logic
│   │   ├── rag_service.py     # Vector DB & retrieval
│   │   ├── llm_service.py     # LLM integration
│   │   ├── reasoning_engine.py # Problem diagnosis
│   │   └── safety_checker.py  # Risk validation
│   │
│   ├── data/                  # Data pipeline
│   │   ├── data_collection.py # Web scraping
│   │   ├── preprocessing.py   # Data cleaning
│   │   └── embeddings.py      # Vector generation
│   │
│   └── tests/                 # Unit tests
│
└── frontend/
    ├── src/
    │   ├── components/        # React components
    │   ├── services/          # API client
    │   └── App.jsx           # Main app
    │
    └── public/               # Static assets
```

## Key Components

### Backend Services

#### RAG Service (`rag_service.py`)

- Manages ChromaDB vector database
- Generates embeddings using sentence-transformers
- Performs semantic search for relevant solutions
- Auto-initializes with sample IT support data

#### LLM Service (`llm_service.py`)

- Integrates with OpenAI GPT and Anthropic Claude
- Formats prompts with context and user info
- Handles API errors and rate limiting
- Falls back to rule-based responses if no API key

#### Reasoning Engine (`reasoning_engine.py`)

- Implements multi-step problem diagnosis
- Rephrases vague queries into technical terms
- Ranks causes by likelihood
- Generates step-by-step solutions
- Tracks conversation context

#### Safety Checker (`safety_checker.py`)

- Validates commands for safety risks
- Detects physical danger keywords
- Warns before data-loss operations
- Recommends professional help when needed

### Frontend Components

#### ChatWindow

- Main chat interface
- Message history management
- Real-time API communication
- Loading states and error handling

#### SolutionSteps

- Interactive step checklist
- Risk level indicators
- Expandable details
- Progress tracking

#### DeviceInfoForm

- Device information collection
- OS and model selection
- Improves solution accuracy

## API Development

### Adding New Endpoints

1. **Define Pydantic Models** (`api/models.py`)

```python
class NewRequest(BaseModel):
    field: str

class NewResponse(BaseModel):
    result: str
```

2. **Create Route Handler** (`api/routes.py`)

```python
@router.post("/new-endpoint", response_model=NewResponse)
async def new_endpoint(request: NewRequest):
    # Implementation
    return NewResponse(result="success")
```

3. **Add Tests** (`tests/test_api.py`)

```python
def test_new_endpoint():
    response = client.post("/api/new-endpoint", json={...})
    assert response.status_code == 200
```

### Extending Knowledge Base

1. **Add Data Source** (`data/data_collection.py`)

```python
async def collect_new_source(self) -> List[Dict]:
    # Scrape or fetch data
    return articles
```

2. **Update Preprocessing** (`data/preprocessing.py`)

```python
def process_new_format(self, data: List[Dict]):
    # Transform to standard format
    return structured_data
```

3. **Regenerate Embeddings**

```powershell
python -m data.embeddings
```

## Testing

### Run All Tests

```powershell
cd backend
pytest tests/ -v
```

### Run Specific Test File

```powershell
pytest tests/test_rag.py -v
```

### Run with Coverage

```powershell
pytest tests/ --cov=services --cov=api --cov-report=html
# Open htmlcov/index.html
```

### Test Categories

- `test_api.py` - Endpoint integration tests
- `test_rag.py` - Vector database tests
- `test_reasoning.py` - Logic engine tests
- `test_safety.py` - Safety validation tests

## Debugging

### Enable Debug Logging

**Backend:**

```python
# api/config.py
log_level: str = "DEBUG"
```

**View Logs:**

```powershell
tail -f backend/logs/app.log
```

### Common Issues

**ChromaDB Lock Error:**

```powershell
# Stop all Python processes, then:
Remove-Item -Recurse backend/data/chroma_db
python -m data.embeddings
```

**LLM API Errors:**

- Check API key in `.env`
- Verify billing and quota
- System works in fallback mode without keys

**Port Already in Use:**

```powershell
# Find process using port 8000
netstat -ano | findstr :8000
# Kill process
taskkill /PID <PID> /F
```

## Performance Optimization

### Backend

1. **Increase RAG Results:**

```python
# api/config.py
rag_top_k: int = 10  # Default: 5
```

2. **Adjust Embedding Batch Size:**

```python
# data/embeddings.py
self.add_to_vector_db(items, batch_size=200)
```

3. **Cache LLM Responses:**

```python
# Implement caching decorator
from functools import lru_cache
```

### Frontend

1. **Enable Production Build:**

```powershell
npm run build
npm run preview
```

2. **Lazy Load Components:**

```javascript
const HeavyComponent = React.lazy(() => import("./Heavy"));
```

## Code Style

### Python (Backend)

- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Max line length: 100 characters

```python
async def example_function(param: str) -> Dict[str, Any]:
    """
    Brief description.

    Args:
        param: Description

    Returns:
        Description of return value
    """
    return {"result": param}
```

### JavaScript (Frontend)

- Use ESLint configuration
- Prefer functional components
- Use PropTypes or TypeScript

```javascript
function Component({ prop }) {
  // Implementation
}

Component.propTypes = {
  prop: PropTypes.string.required,
};
```

## Git Workflow

1. **Create Feature Branch**

```bash
git checkout -b feature/new-feature
```

2. **Make Changes and Commit**

```bash
git add .
git commit -m "feat: Add new feature"
```

3. **Push and Create PR**

```bash
git push origin feature/new-feature
```

### Commit Message Format

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `style:` Formatting

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment instructions.

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic API](https://docs.anthropic.com/)
