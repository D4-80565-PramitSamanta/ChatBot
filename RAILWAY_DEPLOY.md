# 🚂 Deploy to Railway

## ⚠️ If You Get "uvicorn: command not found" Error:

Railway needs to install Python dependencies first. Use one of these methods:

### **Method 1: Use nixpacks.toml (Recommended)**
The `nixpacks.toml` file is already created. Just push and redeploy:
```bash
git add .
git commit -m "Fix Railway deployment"
git push
```
Then in Railway dashboard, click **"Redeploy"**

### **Method 2: Manual Start Command**
In Railway dashboard → **Settings** → **Deploy**:

Change start command to:
```bash
pip install -r requirements.txt && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### **Method 3: Use start.sh**
In Railway dashboard → **Settings** → **Deploy**:

Change start command to:
```bash
bash start.sh
```

---

## Quick Deploy Steps:

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### 2. Deploy on Railway

1. Go to [Railway.app](https://railway.app/)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Railway will auto-detect Python and deploy!

### 3. Set Environment Variables

In Railway dashboard, go to **Variables** tab and add:

```
GEMINI_API_KEY=your_gemini_api_key_here
PORT=8000
```

### 4. Access Your API

Railway will give you a URL like:
```
https://your-app-name.up.railway.app
```

Your Swagger UI will be at:
```
https://your-app-name.up.railway.app/docs
```

---

## 📋 Railway Configuration Files Created:

✅ **Procfile** - Tells Railway how to start the app
✅ **railway.json** - Railway-specific configuration
✅ **runtime.txt** - Specifies Python version
✅ **requirements.txt** - Python dependencies

---

## 🔧 Start Command Used:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

This command:
- Starts the FastAPI app
- Listens on all interfaces (0.0.0.0)
- Uses Railway's dynamic PORT variable

---

## 🌐 Environment Variables Needed:

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Your Google Gemini API key | ✅ Yes |
| `PORT` | Port number (Railway sets this automatically) | ✅ Auto |

---

## 🧪 Test After Deployment:

1. **Health Check:**
   ```
   GET https://your-app.up.railway.app/api/health
   ```

2. **Swagger UI:**
   ```
   https://your-app.up.railway.app/docs
   ```

3. **Chat Endpoint:**
   ```
   POST https://your-app.up.railway.app/api/chat
   {
     "question": "How to cancel a booking?"
   }
   ```

---

## 🔥 Features Deployed:

✅ FastAPI with Swagger UI
✅ Hybrid RAG (Static + Live docs)
✅ Web scraping from https://docs-hotel.prod.zentrumhub.com/
✅ 24 documentation pages indexed
✅ Auto-caching to knowledge-base-dynamic.json
✅ Analytics tracking
✅ Gemini 2.5 Pro integration

---

## 📊 Monitoring:

Railway provides:
- **Logs** - Real-time application logs
- **Metrics** - CPU, Memory, Network usage
- **Deployments** - Deployment history

---

## 🚀 That's It!

Your chatbot is now live and accessible worldwide! 🌍
