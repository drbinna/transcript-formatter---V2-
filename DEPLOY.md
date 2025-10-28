# Deployment Guide - ORU Transcript Formatter

## 🚀 Easiest Option: Render (Recommended)

### Why Render?
- ✅ **Free tier available** - $0/month for hobby projects
- ✅ **Already configured** - `render.yaml` is ready
- ✅ **One-click deploy** - Connect GitHub and deploy
- ✅ **Auto-updates** - Deploys on every push
- ✅ **HTTPS included** - Your app gets a secure URL

### Steps to Deploy:

1. **Push to GitHub** (if not already):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/oru-transcript-formatter.git
   git push -u origin main
   ```

2. **Go to Render Dashboard**:
   - Visit https://render.com
   - Sign up/login (free)

3. **Import from GitHub**:
   - Click "New" → "Blueprint"
   - Paste your GitHub repository URL
   - Render will automatically detect `render.yaml`

4. **Add Environment Variable**:
   - Go to your service settings
   - Add: `ANTHROPIC_API_KEY` = `your-api-key-here`
   - This is required for Claude API calls

5. **Deploy**:
   - Render will build and deploy both services
   - Backend URL: `https://oru-transcript-formatter-backend.onrender.com`
   - Frontend URL: `https://oru-transcript-formatter-frontend.onrender.com`
   - **Total deployment time: ~5-10 minutes**

### Cost:
- **FREE** on Render's hobby plan (spins down after 15 min of inactivity)
- ONLY cost is Anthropic API usage (you pay per API call)

---

## 📊 Alternative Options

### 1. **Replit** (Free & Very Easy)
- Upload code to Replit
- Run `pip install -r backend/requirements.txt`
- Run `npm install` in frontend
- Public URL instantly
- **Cost: FREE**

### 2. **Local Demo** (No hosting needed)
- Run locally on your computer
- Use ngrok to create public tunnel:
  ```bash
  # Terminal 1: Start backend
  cd backend && python3 -m uvicorn main:app --reload
  
  # Terminal 2: Start frontend
  cd frontend && npm run dev
  
  # Terminal 3: Create tunnel
  ngrok http 5173
  ```
- Share ngrok URL for demo
- **Cost: FREE**

### 3. **Fly.io** (Free tier available)
- Similar to Render, has free tier
- Requires Docker setup
- **Cost: FREE for small apps**

---

## 💰 API Cost Estimation

**Anthropic Claude API costs:**
- Claude Sonnet 4.5: ~$3 per million input tokens, $15 per million output tokens
- Typical transcript: ~15,000 tokens
- **Cost per transcript: ~$0.05-0.10**
- **100 transcripts = ~$5-10**

**Demo recommendation:**
- Show 1-2 real transcripts during demo
- **Total API cost: ~$0.10-0.20**

---

## 🎯 Quick Demo Script

**What to show:**
1. ✅ Upload raw `.txt` file
2. ✅ Watch progress bar fill up
3. ✅ Download formatted `.docx`
4. ✅ Open in Word to show:
   - Professional formatting
   - Bold speaker names
   - Italic titles
   - Proper spacing
   - Complete content (198 segments!)

**Duration:** 2-3 minutes

---

## 🏆 Recommended: Render + Local Backup

**For Demo:**
- **Primary:** Deploy to Render for online demo
- **Backup:** Keep local version running in case Render is slow
- **Demo both** to show it works anywhere

**Setup time:** ~10 minutes
**Ongoing cost:** ~$0 (only pay for API calls you use)

