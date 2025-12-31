# Railway Deployment Guide - Startup Analyzer

**Complete guide for deploying the Startup Analyzer to Railway (beginner-friendly)**

---

## Prerequisites

Before starting, you'll need:

1. ✅ GitHub account (to connect your code)
2. ✅ Railway account (we'll create this)
3. ✅ OpenRouter API key
4. ✅ Tavily API key
5. ✅ Credit card for Railway (free tier available, but requires card)

---

## Step 1: Prepare Your Code for Deployment

### 1.1 Create `.gitignore` file

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
*.egg-info/
dist/
build/

# Environment
.env
.env.local
.env.production

# Data
data/vector_store/
*.faiss
*.pkl

# Logs
*.log
logs/
backend.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
frontend/dist/
frontend/build/

# Test results
tests/evaluation/eval_results_*.json

# Temporary
*.tmp
temp/
EOF
```

### 1.2 Create `Procfile` for Backend

```bash
cat > Procfile << 'EOF'
web: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
EOF
```

### 1.3 Create `railway.json` Configuration

```bash
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "RAILPACK"
  },
  "deploy": {
    "startCommand": "uvicorn src.api.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF
```

**Note:** Railway now uses **RAILPACK** as their recommended build system (replaces the deprecated nixpacks).

### 1.4 Update `requirements.txt` (add production server)

```bash
cat >> requirements.txt << 'EOF'

# Production server
gunicorn>=21.2.0
EOF
```

### 1.5 Create Frontend Build Configuration

Edit `frontend/package.json` to add build command if not present:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

### 1.6 Update Frontend API URL for Production

Create `frontend/.env.production`:

```bash
cat > frontend/.env.production << 'EOF'
VITE_API_URL=https://your-backend-url.railway.app
EOF
```

**Note:** We'll update this with the actual URL after deploying the backend.

---

## Step 2: Push Code to GitHub

### 2.1 Initialize Git Repository (if not already)

```bash
# In project root
git init
git add .
git commit -m "Initial commit - Startup Analyzer ready for deployment"
```

### 2.2 Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `startup-analyzer`
3. Description: "AI-powered startup idea analyzer"
4. **Private** or Public (your choice)
5. Click "Create repository"

### 2.3 Push to GitHub

```bash
# Replace with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/startup-analyzer.git
git branch -M main
git push -u origin main
```

---

## Step 3: Create Railway Account

### 3.1 Sign Up

1. Go to https://railway.app
2. Click "Start a New Project" or "Login"
3. Sign up with GitHub (recommended) or email
4. Verify your email
5. Add a credit card (required, but free tier includes $5/month credit)

### 3.2 Install Railway CLI (Optional but Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Or using curl
curl -fsSL https://railway.app/install.sh | sh

# Login
railway login
```

---

## Step 4: Deploy Backend to Railway

### 4.1 Create New Project

**Option A: Via Railway Dashboard (Recommended for beginners)**

1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub
5. Select your `startup-analyzer` repository
6. Railway will detect it's a Python project

**Option B: Via Railway CLI**

```bash
# In project root
railway init
railway link
```

### 4.2 Configure Environment Variables

In Railway Dashboard:

1. Click on your project
2. Go to "Variables" tab
3. Add the following variables:

```
# Required
OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY_HERE
TAVILY_API_KEY=tvly-YOUR_KEY_HERE
LLM_MODEL=openai/gpt-4o

# Optional but recommended
LANGSMITH_API_KEY=lsv2_YOUR_KEY_HERE
LANGSMITH_PROJECT=startup-analyzer
APP_ENV=production
LOG_LEVEL=INFO

# Railway provides these automatically
PORT=8000
```

### 4.3 Configure Build Settings

1. In Railway Dashboard, go to "Settings"
2. **Build Command:** (leave empty, RAILPACK auto-detects)
3. **Start Command:** `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
4. **Root Directory:** `.` (project root)

**Note:** Railway will use RAILPACK (specified in `railway.json`) to automatically detect and build your Python application.

### 4.4 Deploy

Railway will automatically deploy when you push to GitHub. To trigger manually:

```bash
# Via CLI
railway up

# Or push to GitHub
git push origin main
```

### 4.5 Get Backend URL

1. In Railway Dashboard, go to "Settings"
2. Click "Generate Domain" under "Domains"
3. Your backend will be at: `https://your-project-name.up.railway.app`
4. Copy this URL - you'll need it for the frontend!

### 4.6 Test Backend

```bash
# Check health
curl https://your-project-name.up.railway.app/health

# Should return: {"status":"healthy"}

# Check API docs
# Open: https://your-project-name.up.railway.app/docs
```

---

## Step 5: Deploy Frontend to Railway

### 5.1 Update Frontend API URL

Edit `frontend/vite.config.js` to use environment variable:

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

Update `frontend/.env.production`:

```bash
# Replace with your actual Railway backend URL
VITE_API_URL=https://your-project-name.up.railway.app
```

Also update the `useSSE` hook to use the backend URL:

Edit `frontend/src/hooks/useSSE.js`:

```javascript
// At the top, get API URL from environment
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

// In the connect function, use full URL:
const response = await fetch(`${API_BASE_URL}${url}`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(body),
});
```

### 5.2 Build Frontend Locally (Test)

```bash
cd frontend
npm install
npm run build

# Test the build
npm run preview
```

### 5.3 Option A: Deploy Frontend as Separate Railway Service

**Create new Railway service:**

1. In Railway Dashboard, same project
2. Click "New Service"
3. Select "Empty Service"
4. Name it "startup-analyzer-frontend"

**Configure Frontend Service:**

1. Go to "Settings"
2. **Build Command:** `cd frontend && npm install && npm run build`
3. **Start Command:** `cd frontend && npm run preview -- --host 0.0.0.0 --port $PORT`
4. **Root Directory:** `.`

**Add Environment Variable:**
```
VITE_API_URL=https://your-backend-url.up.railway.app
```

**Generate Domain:**
1. Go to "Settings" > "Domains"
2. Click "Generate Domain"
3. Your frontend: `https://your-frontend-name.up.railway.app`

### 5.4 Option B: Serve Frontend from Backend (Simpler)

**Modify `src/api/main.py` to serve static files:**

```python
# Add at the top
from fastapi.staticfiles import StaticFiles
import os

# After creating the app, before including routers
# Serve static files from frontend/dist
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
```

**Build frontend and include in deployment:**

```bash
cd frontend
npm run build
cd ..

# Commit and push
git add .
git commit -m "Add frontend static build"
git push origin main
```

**Access:**
- Frontend: `https://your-backend-url.up.railway.app/`
- API Docs: `https://your-backend-url.up.railway.app/docs`

---

## Step 6: Setup RAG Vector Store on Railway

Railway doesn't persist files by default. You need to either:

### Option A: Use Railway Volume (Recommended)

1. In Railway Dashboard, go to your backend service
2. Click "Settings" > "Volumes"
3. Click "Add Volume"
4. Mount path: `/app/data`
5. This persists your vector store

### Option B: Rebuild on Startup

Add to `Procfile`:

```
release: python scripts/build_vector_store.py
web: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
```

Create `scripts/build_vector_store.py` to check if vector store exists:

```python
if not os.path.exists('data/vector_store/index.faiss'):
    # Build vector store
    # ...
```

### Option C: Build Locally and Commit

```bash
# Create knowledge base
mkdir -p data/knowledge_base
# Add your marketing framework documents

# Build vector store
python scripts/build_vector_store.py

# Add to git (usually not recommended, but works)
git add data/vector_store/
git commit -m "Add pre-built vector store"
git push
```

---

## Step 7: Configure CORS for Production

Update `src/api/main.py` to allow your frontend domain:

```python
# Update CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://your-frontend-name.up.railway.app",  # Production frontend
        "https://your-backend-name.up.railway.app",  # Production backend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Or allow all (less secure but simpler):

```python
allow_origins=["*"],
```

---

## Step 8: Monitoring and Logs

### View Logs

**Via Dashboard:**
1. Railway Dashboard > Your Service
2. Click "Deployments"
3. Click on latest deployment
4. View logs in real-time

**Via CLI:**
```bash
railway logs
```

### Monitor Resources

1. Railway Dashboard > Your Service
2. Click "Metrics" tab
3. View CPU, Memory, Network usage

### Set Up Alerts

1. Railway Dashboard > Project Settings
2. Go to "Integrations"
3. Add Slack/Discord webhook for alerts

---

## Step 9: Custom Domain (Optional)

### 9.1 Add Custom Domain

1. Railway Dashboard > Your Service
2. Go to "Settings" > "Domains"
3. Click "Custom Domain"
4. Enter your domain: `app.yourdomain.com`

### 9.2 Configure DNS

Add CNAME record in your DNS provider:

```
Type: CNAME
Name: app (or your subdomain)
Value: your-project-name.up.railway.app
TTL: Auto or 3600
```

### 9.3 Wait for DNS Propagation

Can take 5 minutes to 48 hours. Check with:

```bash
dig app.yourdomain.com
```

---

## Step 10: Database Setup (Optional)

If you want to store analysis results:

### 10.1 Add PostgreSQL

1. Railway Dashboard > Your Project
2. Click "New Service"
3. Select "Database" > "PostgreSQL"
4. Railway automatically creates `DATABASE_URL` variable

### 10.2 Update Backend

Add to `requirements.txt`:

```
psycopg2-binary>=2.9.9
sqlalchemy>=2.0.23
```

Create database models and store results (future enhancement).

---

## Troubleshooting

### Build Fails

**Check logs:**
```bash
railway logs
```

**Common issues:**
- Missing dependencies in `requirements.txt`
- Python version mismatch
- Missing environment variables

**Fix:**
- Ensure all imports are in `requirements.txt`
- Specify Python version in `runtime.txt`:
  ```
  python-3.10.13
  ```

### App Crashes

**Check logs for errors:**
```bash
railway logs --tail 100
```

**Common issues:**
- Missing API keys
- Port binding issues
- Vector store not found

**Fix:**
- Verify all environment variables
- Use `$PORT` provided by Railway
- Rebuild vector store or use volume

### CORS Errors

**Symptoms:** Frontend can't connect to backend

**Fix:**
```python
# In src/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for testing
    # ... rest
)
```

### High Costs

**Monitor usage:**
- Railway Dashboard > Metrics
- Check request counts
- Monitor token usage

**Optimize:**
- Use cheaper models for testing
- Add rate limiting
- Cache results
- Set monthly budget alerts

---

## Cost Estimation

### Railway Costs

**Free Tier:**
- $5 credit per month
- Hobby plan: $5/month after trial
- Pay-as-you-go after that

**Typical Usage:**
- Backend: ~$5-10/month (low traffic)
- Frontend: ~$0-5/month (if separate)
- Database: ~$5/month (if added)

**Expected:** ~$10-20/month for moderate usage

### API Costs (OpenRouter + Tavily)

**Per Analysis:**
- GPT-4o: ~$0.08-0.15
- Tavily searches: ~$0.01-0.02
- **Total per analysis:** ~$0.10-0.20

**Monthly estimates:**
- 50 analyses: ~$5-10
- 500 analyses: ~$50-100
- 5000 analyses: ~$500-1000

---

## Security Best Practices

### 1. Environment Variables

✅ Never commit `.env` files
✅ Use Railway's environment variables
✅ Rotate API keys regularly

### 2. API Rate Limiting

Add rate limiting to prevent abuse:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/analyze")
@limiter.limit("10/hour")
async def analyze(...):
    ...
```

### 3. Authentication (Future)

Consider adding:
- API keys for clients
- User authentication
- Usage quotas

---

## Deployment Checklist

Before going live:

- [ ] All environment variables set
- [ ] CORS configured correctly
- [ ] Vector store available
- [ ] Health endpoint responding
- [ ] API docs accessible
- [ ] Frontend loading correctly
- [ ] Test analysis works end-to-end
- [ ] Logs show no errors
- [ ] Monitoring set up
- [ ] Domain configured (if custom)
- [ ] Budget alerts configured

---

## Quick Commands Reference

```bash
# Railway CLI
railway login
railway init
railway link
railway up
railway logs
railway status
railway open

# Git deployment
git add .
git commit -m "Deploy updates"
git push origin main

# Local testing
uvicorn src.api.main:app --reload
cd frontend && npm run dev

# Build frontend
cd frontend && npm run build
```

---

## Next Steps After Deployment

1. **Test the deployment**
   - Run a few test analyses
   - Check all agents work
   - Verify streaming works
   - Monitor costs

2. **Share the link**
   - Send URL to users
   - Get feedback
   - Monitor usage

3. **Set up monitoring**
   - Railway metrics
   - LangSmith traces (if enabled)
   - Error tracking

4. **Plan for scaling**
   - Monitor response times
   - Check token usage
   - Consider caching
   - Plan database if needed

---

## Support

**Railway Documentation:**
- https://docs.railway.app

**Railway Discord:**
- https://discord.gg/railway

**Project Issues:**
- Check Railway logs first
- Review environment variables
- Test locally to isolate issues

---

**You're ready to deploy! 🚀**

Start with Step 1 and work through each section. Feel free to ask questions at any step!
