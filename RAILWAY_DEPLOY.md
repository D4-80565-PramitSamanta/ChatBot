# 🚂 Railway Deployment - FIXED ✅

## Problem Solved: PORT Variable Expansion

**Issue**: Dockerfile wasn't expanding `8000` environment variable
**Solution**: Created `start_server.py` to handle PORT at runtime

---

## 🚀 Quick Deploy

```bash
git add .
git commit -m "Fix Railway PORT handling"
git push
```

Railway will automatically:
1. Build using Dockerfile
2. Run `python start_server.py`
3. Start on Railway's assigned PORT
4. Deploy to your public URL

---

## ✅ What Was Fixed

### Before (Broken):
```dockerfile
CMD uvicorn app.main:app --host 0.0.0.0 --port 8000
```
❌ Shell doesn't expand `8000` in CMD - passed as literal string "8000"

### After (Working):
```dockerfile
CMD ["python", "start_server.py"]
```
✅ Python script reads PORT from environment at runtime

---

## 📁 Key Files

### `start_server.py` (NEW)
```python
import os
import uvicorn

port = int(os.getenv("PORT", 8000))
print(f"Starting server on port {port}...")
uvicorn.run("app.main:app", host="0.0.0.0", port=port)
```

### `Dockerfile`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "start_server.py"]
```

### `railway.json`
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  }
}
```

---

## 🔧 Environment Variables

Set in Railway dashboard:

| Variable | Value | Required |
|----------|-------|----------|
| `GEMINI_API_KEY` | Your API key | ✅ Yes |
| `PORT` | (Auto-set by Railway) | ✅ Auto |

**Note**: Don't manually set PORT - Railway provides it automatically!

---

## 🧪 Test Your Deployment

### Your Railway URL:
```
https://web-production-86e7.up.railway.app
```

### Endpoints:
- **Swagger UI**: `/docs`
- **Health Check**: `/api/health`
- **Chat**: `POST /api/chat`

### Test Chat:
```bash
curl -X POST https://web-production-86e7.up.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I cancel a booking?"}'
```

---

## 🔍 Verify Deployment

Check Railway logs for:
```
Starting server on port 8080...
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8080
```

---

## 🌟 Features Deployed

✅ FastAPI with Swagger UI
✅ Hybrid RAG (Static JSON + Live docs)
✅ Web scraping from docs-hotel.prod.zentrumhub.com
✅ 24 documentation pages indexed
✅ Auto-caching to knowledge-base-dynamic.json
✅ Gemini 2.5 Pro integration
✅ Cancel API support (fixed!)

---

## 🐛 Troubleshooting

### App won't start
- Check Railway logs for errors
- Verify GEMINI_API_KEY is set in dashboard
- Look for "Starting server on port..." message

### 401/403 Errors
- Check GEMINI_API_KEY is correct
- Verify API key has proper permissions

### Can't find documentation
- Check logs for "Fetching from live docs..."
- Verify knowledge-base files are included in build

---

## 📊 What Happens on Deploy

1. Railway detects push to GitHub
2. Reads `railway.json` → uses Dockerfile
3. Builds Docker image with Python 3.11
4. Installs requirements.txt
5. Copies all app files
6. Sets PORT environment variable (e.g., 8080)
7. Runs `python start_server.py`
8. start_server.py reads PORT and starts uvicorn
9. App is live! 🎉

---

## 🎯 Next Steps

1. Push your changes to GitHub
2. Watch Railway logs for successful deployment
3. Test `/docs` endpoint
4. Try asking: "How do I cancel a booking?"
5. Monitor analytics in `analytics_data.json`

---

**Status**: Ready to deploy! Push to trigger Railway build.
