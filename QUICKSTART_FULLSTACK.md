# 🚀 Quick Start - Full Stack Startup Analyzer

**Complete guide to running the backend + frontend together**

---

## Prerequisites

1. **Python 3.10+** with pip
2. **Node.js 18+** with npm
3. **API Keys:**
   - OpenRouter API key (for GPT-4o)
   - Tavily API key (for web search)

---

## Initial Setup (First Time Only)

### 1. Clone/Navigate to Project
```bash
cd /data/data/com.termux/files/home/lik/startup_analyzer
```

### 2. Create Environment File
```bash
cat > .env << 'EOF'
# LLM Provider
OPENROUTER_API_KEY=your_openrouter_key_here
LLM_MODEL=openai/gpt-4o

# Tools
TAVILY_API_KEY=your_tavily_key_here

# Optional - Observability
LANGSMITH_API_KEY=your_langsmith_key_here  # Optional
LANGSMITH_PROJECT=startup-analyzer
EOF
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Build RAG Vector Store
```bash
# Create knowledge base directory
mkdir -p data/knowledge_base

# Add some marketing framework documents (example)
cat > data/knowledge_base/frameworks.txt << 'EOF'
# Marketing Frameworks

## Porter's Five Forces
Analysis of competitive forces...

## Blue Ocean Strategy
Creating uncontested market space...

## Jobs To Be Done (JTBD)
Understanding customer needs...

Add your own marketing frameworks here...
EOF

# Build the vector store
python scripts/build_vector_store.py
```

### 5. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## Running the Application

### Option 1: Two Terminals (Recommended)

**Terminal 1 - Backend:**
```bash
# From project root
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
# From project root
cd frontend
npm run dev
```

### Option 2: Background Process (Alternative)

**Start Backend in Background:**
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend running with PID: $BACKEND_PID"
```

**Start Frontend:**
```bash
cd frontend
npm run dev
```

**Stop Backend Later:**
```bash
kill $BACKEND_PID
```

---

## Access the Application

Once both servers are running:

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | Main application UI |
| **Backend API** | http://localhost:8000 | API endpoints |
| **API Docs** | http://localhost:8000/docs | Swagger documentation |
| **Health Check** | http://localhost:8000/health | Service status |
| **Metrics** | http://localhost:8000/metrics | Prometheus metrics |

---

## Using the Application

### 1. Open Frontend
Navigate to http://localhost:3000 in your browser

### 2. Enter Your Idea
- **X Brand:** The established company you want to emulate (e.g., "Uber", "Netflix")
- **Y Market:** The target market (e.g., "Dog Walkers", "Fitness Classes")
- **Description:** Optional additional context

### 3. Click Examples (Quick Start)
Click any example button to auto-fill the form:
- Uber for Dog Walkers
- Netflix for Fitness Classes
- Airbnb for Office Spaces

### 4. Analyze
Click the "🚀 Analyze Idea" button

### 5. Watch Real-Time Progress
- See each agent work in real-time:
  - 🔍 **Brand Analyst** - Deconstructing brand DNA
  - 📊 **Market Researcher** - Analyzing market
  - 🤔 **Skeptic** - Critical evaluation
  - 🎯 **Strategist** - GTM strategy

### 6. View Results
- **Viability Score** (0-10)
- **Brand Analysis** - Core strengths, business model
- **Market Research** - Competition, opportunities
- **Critical Analysis** - Concerns and suggestions
- **GTM Strategy** - Complete go-to-market plan
- **Metrics** - Duration, cost, tokens used

---

## Troubleshooting

### Backend Won't Start

**Error: `Address already in use`**
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn src.api.main:app --port 8001
```

**Error: `No module named 'src'`**
```bash
# Ensure you're in the project root
pwd  # Should show .../startup_analyzer

# Reinstall dependencies
pip install -r requirements.txt
```

**Error: `OPENROUTER_API_KEY not found`**
```bash
# Check .env file exists
cat .env

# Verify it's in the project root
ls -la .env
```

### Frontend Won't Start

**Error: `Cannot find module 'react'`**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Error: `Port 3000 already in use`**
```bash
# Frontend will auto-suggest another port (e.g., 3001)
# Or kill the process
lsof -ti:3000 | xargs kill -9
```

**Error: `Failed to fetch /api/analyze/stream`**
- Ensure backend is running on port 8000
- Check backend logs for errors
- Verify API is accessible: curl http://localhost:8000/health

### Analysis Fails

**Error: `Invalid API key`**
- Check your OpenRouter API key is correct
- Verify it has credits available
- Test with: curl https://openrouter.ai/api/v1/models -H "Authorization: Bearer YOUR_KEY"

**Error: `Tavily search failed`**
- Check your Tavily API key
- Verify at: https://tavily.com

**Slow Response**
- Analysis typically takes 30-60 seconds
- Check your internet connection
- Monitor backend logs for progress

### SSE Stream Not Connecting

**Browser shows connection error**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Filter by "analyze/stream"
4. Check response status
5. Verify backend is sending SSE events

**No real-time updates**
- Refresh the page
- Check CORS is enabled (should be by default)
- Try a different browser

---

## Testing

### Quick Test

```bash
# Terminal 1: Start backend
uvicorn src.api.main:app --reload --port 8000

# Terminal 2: Test API
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"x_brand": "Uber", "y_market": "Dog Walkers"}'

# Terminal 3: Test frontend
cd frontend && npm run dev
# Then open http://localhost:3000 in browser
```

### Full Test Script

```bash
# Backend test
python scripts/test_api.py

# Workflow test
python scripts/test_workflow.py
```

---

## Development Mode

### Backend Hot Reload
The `--reload` flag automatically restarts on code changes:
```bash
uvicorn src.api.main:app --reload --port 8000
```

### Frontend Hot Module Replacement
Vite provides instant HMR - changes appear without refresh:
```bash
cd frontend && npm run dev
```

---

## Production Build

### Backend (FastAPI)
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (React)
```bash
cd frontend

# Build for production
npm run build

# Output in dist/ folder
ls -la dist/

# Preview build
npm run preview
```

### Serve Both Together
```bash
# Option 1: FastAPI serves static files
# Add to src/api/main.py:
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

# Option 2: Use nginx to serve both
# See deployment docs
```

---

## Environment Variables

### Backend (.env)
```bash
# Required
OPENROUTER_API_KEY=sk-or-v1-...
TAVILY_API_KEY=tvly-...
LLM_MODEL=openai/gpt-4o

# Optional
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_PROJECT=startup-analyzer
APP_ENV=development
LOG_LEVEL=INFO
```

### Frontend (optional)
```bash
# If you need custom API URL
VITE_API_URL=http://your-backend-url.com
```

---

## Common Commands Reference

### Backend
```bash
# Start development
uvicorn src.api.main:app --reload --port 8000

# Test workflow
python scripts/test_workflow.py

# Test API
python scripts/test_api.py

# Build vector store
python scripts/build_vector_store.py

# View logs
tail -f backend.log
```

### Frontend
```bash
# Install dependencies
npm install

# Start development
npm run dev

# Build production
npm run build

# Preview production
npm run preview

# Check for issues
npm run lint  # If configured
```

---

## Architecture Overview

```
User Browser (localhost:3000)
    ↓
Vite Dev Server (Frontend)
    ↓
[Proxy] /api/* → localhost:8000
    ↓
FastAPI (Backend)
    ↓
LangGraph Workflow
    ↓
┌─────────────────────────────────┐
│ Analyst → Researcher → Skeptic  │
│     ↓                            │
│ [Loop if needed]                 │
│     ↓                            │
│ Strategist                       │
└─────────────────────────────────┘
    ↓
OpenRouter API (GPT-4o)
Tavily Search API
RAG Vector Store (FAISS)
```

---

## Performance Tips

1. **First Analysis Slow?**
   - First request loads models
   - Subsequent requests faster (model cached)

2. **Reduce Costs**
   - Use smaller models for testing
   - Set `LLM_MODEL=openai/gpt-3.5-turbo`
   - Limit token counts in agent prompts

3. **Speed Up Development**
   - Backend: Use `--reload` for hot reload
   - Frontend: Vite HMR is instant
   - Keep both running during development

---

## Next Steps

After running the application:

1. **Try Different Ideas**
   - Test various "X for Y" combinations
   - Observe quality loops in action
   - Review viability scores

2. **Explore Observability**
   - Check metrics at /metrics
   - View structured logs
   - (Optional) Set up LangSmith tracing

3. **Customize**
   - Add your own marketing frameworks to RAG
   - Adjust agent prompts
   - Modify UI styling

4. **Deploy**
   - Follow deployment guide for Railway
   - Configure production environment
   - Set up monitoring

---

## Support

- **Documentation:** See FINAL_STATUS.md for full project status
- **API Docs:** http://localhost:8000/docs (when running)
- **Frontend Docs:** frontend/README.md
- **Issues:** Check logs in backend.log or browser console

---

**🎉 You're all set! Enjoy analyzing startup ideas with AI!**
