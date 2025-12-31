# Railway Deployment Checklist

**Quick checklist to deploy your Startup Analyzer to Railway**

---

## Pre-Deployment

- [ ] OpenRouter API key ready
- [ ] Tavily API key ready
- [ ] GitHub account ready
- [ ] Railway account created (with credit card on file)
- [ ] Code tested locally and working

---

## Step-by-Step Deployment

### 1. Prepare Code
- [ ] Create `.gitignore` ✅ (already created)
- [ ] Create `Procfile` ✅ (already created)
- [ ] Create `railway.json` ✅ (already created)
- [ ] Create `runtime.txt` ✅ (already created)
- [ ] Update `requirements.txt` with gunicorn ✅ (already created)

### 2. Push to GitHub
```bash
# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for Railway deployment"

# Create GitHub repo at: https://github.com/new
# Name it: startup-analyzer

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/startup-analyzer.git
git branch -M main
git push -u origin main
```

- [ ] Code pushed to GitHub
- [ ] Repository URL: ___________________________

### 3. Create Railway Project

**Go to:** https://railway.app/dashboard

- [ ] Sign up / Log in to Railway
- [ ] Add credit card (required even for free tier)
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Authorize Railway GitHub access
- [ ] Select `startup-analyzer` repository

### 4. Configure Backend

**In Railway Dashboard > Your Service > Variables:**

Add these environment variables:

- [ ] `OPENROUTER_API_KEY` = sk-or-v1-_______________
- [ ] `TAVILY_API_KEY` = tvly-_______________
- [ ] `LLM_MODEL` = openai/gpt-4o
- [ ] `APP_ENV` = production
- [ ] `LOG_LEVEL` = INFO

**Optional but recommended:**
- [ ] `LANGSMITH_API_KEY` = lsv2-_______________
- [ ] `LANGSMITH_PROJECT` = startup-analyzer

### 5. Generate Backend Domain

**In Railway Dashboard > Settings > Domains:**

- [ ] Click "Generate Domain"
- [ ] Copy your backend URL: ___________________________
- [ ] Test health: `curl https://YOUR-URL.up.railway.app/health`
- [ ] Should return: `{"status":"healthy"}`

### 6. Update Frontend for Production

**Edit `frontend/.env.production`:**

```bash
VITE_API_URL=https://YOUR-BACKEND-URL.up.railway.app
```

- [ ] Updated `frontend/.env.production` with actual backend URL
- [ ] Commit and push changes:
  ```bash
  git add frontend/.env.production
  git commit -m "Update frontend API URL for production"
  git push origin main
  ```

### 7. Deploy Frontend

**Option A: Serve from Backend (Simpler)**

1. Build frontend locally:
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

2. Update `src/api/main.py` (add after app creation):
   ```python
   from fastapi.staticfiles import StaticFiles
   import os

   # Serve frontend static files
   frontend_dist = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
   if os.path.exists(frontend_dist):
       app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
   ```

3. Commit and push:
   ```bash
   git add .
   git commit -m "Add frontend static build"
   git push origin main
   ```

- [ ] Frontend built locally
- [ ] Updated `src/api/main.py` to serve static files
- [ ] Committed and pushed to GitHub
- [ ] Railway redeployed automatically

**Option B: Separate Frontend Service (Advanced)**

- [ ] Create new Railway service
- [ ] Configure build command: `cd frontend && npm install && npm run build`
- [ ] Configure start command: `cd frontend && npm run preview -- --host 0.0.0.0 --port $PORT`
- [ ] Generate domain for frontend
- [ ] Update CORS in backend to allow frontend domain

### 8. Setup Vector Store

**Choose one option:**

**Option A: Railway Volume (Recommended)**
- [ ] Go to Railway Dashboard > Settings > Volumes
- [ ] Add Volume
- [ ] Mount path: `/app/data`

**Option B: Build on Startup**
- [ ] Add release command to Procfile:
  ```
  release: python scripts/build_vector_store.py
  web: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
  ```

**Option C: Commit Pre-built**
- [ ] Build locally: `python scripts/build_vector_store.py`
- [ ] Add to git: `git add data/vector_store/`
- [ ] Commit: `git commit -m "Add vector store"`
- [ ] Push: `git push`

### 9. Test Deployment

- [ ] Backend health check: https://YOUR-URL.up.railway.app/health
- [ ] API docs accessible: https://YOUR-URL.up.railway.app/docs
- [ ] Frontend loading: https://YOUR-URL.up.railway.app/
- [ ] Run test analysis through frontend
- [ ] Check agents work correctly
- [ ] Verify SSE streaming works
- [ ] Check Railway logs for errors

### 10. Monitor Deployment

- [ ] Check Railway Dashboard > Metrics
- [ ] Verify no errors in logs
- [ ] Monitor resource usage (CPU, Memory)
- [ ] Check costs in Railway billing

---

## Post-Deployment

### URLs to Save

- [ ] Backend URL: ___________________________
- [ ] Frontend URL: ___________________________
- [ ] API Docs: ___________________________/docs
- [ ] Railway Dashboard: https://railway.app/dashboard

### Optional Enhancements

- [ ] Set up custom domain
- [ ] Configure DNS records
- [ ] Add rate limiting
- [ ] Set up monitoring alerts
- [ ] Enable LangSmith tracing
- [ ] Add PostgreSQL for result storage

---

## Troubleshooting

**If deployment fails:**

1. Check Railway logs:
   - Dashboard > Deployments > Latest > Logs

2. Common issues:
   - Missing environment variables → Add in Variables tab
   - Port binding → Ensure using `$PORT` from Railway
   - Dependencies → Check `requirements.txt` complete
   - Vector store → Use Volume or rebuild on startup

3. Test locally first:
   ```bash
   uvicorn src.api.main:app --reload
   ```

---

## Cost Monitoring

**Expected monthly costs:**

- Railway: $5-15/month (Hobby plan)
- OpenRouter (GPT-4o): $0.10 per analysis
- Tavily: $0.01 per analysis
- **Total per analysis:** ~$0.11-0.20

**For 100 analyses/month:**
- Railway: ~$10
- APIs: ~$11-20
- **Total: ~$21-30/month**

**Set budget alerts in Railway Dashboard!**

---

## Success Criteria

✅ Backend deployed and responding
✅ Frontend accessible
✅ Test analysis completes successfully
✅ Agents work in correct sequence
✅ SSE streaming shows real-time updates
✅ Results display correctly
✅ No errors in Railway logs
✅ Costs within expected range

---

## Quick Commands

```bash
# View logs
railway logs

# Redeploy
git push origin main

# Check status
railway status

# Open in browser
railway open
```

---

**When all items are checked, your deployment is complete! 🎉**
