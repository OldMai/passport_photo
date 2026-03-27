# Deployment Guide - Passport Photo Processor

This guide covers three ways to deploy the application for your friend to test.

## Option 1: ngrok (Quickest - 2 minutes)

**Best for**: Immediate sharing while your computer is on
**Cost**: Free
**Setup time**: 2 minutes

### Steps:

1. **Install ngrok**:
   ```bash
   # macOS
   brew install ngrok

   # Or download from https://ngrok.com/download
   ```

2. **Make sure both servers are running**:
   ```bash
   # Terminal 1 - Backend (already running)
   cd backend
   ./venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

   # Terminal 2 - Frontend (already running)
   cd frontend
   npm run dev
   ```

3. **Expose frontend with ngrok**:
   ```bash
   # Terminal 3
   ngrok http 5173
   ```

4. **Update backend CORS**:
   - Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)
   - Edit `backend/.env` or `backend/app/config.py`:
     ```python
     ALLOWED_ORIGINS = "https://abc123.ngrok.io"
     ```
   - Restart backend server

5. **Share the ngrok URL** with your friend!

**Limitations**:
- Your computer must stay on
- URL changes each time you restart ngrok (free tier)
- Session timeout after 8 hours (free tier)

---

## Option 2: Render.com (Free Cloud Hosting)

**Best for**: Persistent deployment without keeping your computer on
**Cost**: Free
**Setup time**: 30-60 minutes
**Limitations**: 512MB RAM (may be slow), spins down after 15min inactive

### Prerequisites:
1. GitHub account
2. Push this project to GitHub

### Steps:

#### A. Push to GitHub

```bash
cd /Users/xinyuzhao/Project/passport_photo

# Initialize git (if not already)
git init

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
venv/
__pycache__/
*.pyc
.env

# Node
node_modules/
dist/

# Storage
backend/storage/uploads/*
backend/storage/processed/*
backend/storage/print_layouts/*
!backend/storage/.gitkeep

# Logs
*.log

# OS
.DS_Store
EOF

# Add all files
git add .
git commit -m "Initial commit - Passport Photo Processor"

# Create GitHub repo and push
# (Follow GitHub's instructions to create a new repo)
git remote add origin https://github.com/YOUR_USERNAME/passport-photo.git
git branch -M main
git push -u origin main
```

#### B. Deploy Backend on Render.com

1. Go to https://render.com and sign up
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `passport-photo-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

5. Add Environment Variables:
   - `DEBUG`: `False`
   - `ALLOWED_ORIGINS`: (leave blank for now, will add frontend URL later)

6. Add Disk (for file storage):
   - Go to **"Disks"** tab
   - Click **"Add Disk"**
   - **Mount Path**: `/app/storage`
   - **Size**: `1 GB`

7. Click **"Create Web Service"**

8. **Wait for deployment** (~5-10 minutes)

9. **Copy the backend URL** (e.g., `https://passport-photo-backend.onrender.com`)

#### C. Deploy Frontend on Render.com

1. Click **"New +"** → **"Static Site"**
2. Connect the same GitHub repository
3. Configure:
   - **Name**: `passport-photo-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. Add Environment Variable:
   - `VITE_API_URL`: `https://passport-photo-backend.onrender.com`

5. Click **"Create Static Site"**

6. **Wait for deployment** (~3-5 minutes)

7. **Copy the frontend URL** (e.g., `https://passport-photo-frontend.onrender.com`)

#### D. Update Backend CORS

1. Go back to your backend service
2. Update Environment Variables:
   - `ALLOWED_ORIGINS`: `https://passport-photo-frontend.onrender.com`
3. Click **"Manual Deploy"** → **"Deploy latest commit"**

#### E. Test & Share!

- Visit your frontend URL
- Upload a test photo
- Share the URL with your friend!

**Important Notes**:
- Free tier spins down after 15 min of inactivity (30s cold start)
- 512MB RAM is tight - processing may be slow or fail
- If it fails, consider Railway.app ($5 credit)

---

## Option 3: Railway.app (Best Performance)

**Best for**: Better performance and reliability
**Cost**: $5/month (free trial)
**Setup time**: 20-30 minutes

### Steps:

1. Go to https://railway.app and sign up with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Railway will auto-detect `docker-compose.yml`
5. Configure environment variables:
   - For backend: Add `ALLOWED_ORIGINS` with frontend URL
   - For frontend: Add `VITE_API_URL` with backend URL
6. Deploy both services
7. Railway provides URLs for both services

**Advantages**:
- Better RAM allocation (no 512MB limit)
- No spin-down
- Faster processing
- $5 credit lasts ~1-2 weeks for testing

---

## Option 4: Local Network (Same WiFi)

**Best for**: If your friend is nearby
**Cost**: Free
**Setup time**: 1 minute

### Steps:

1. Find your local IP address:
   ```bash
   # macOS/Linux
   ifconfig | grep "inet "

   # Look for something like 192.168.1.xxx
   ```

2. Share this URL with your friend:
   ```
   http://YOUR_IP_ADDRESS:5173
   ```

3. Make sure both are on the same WiFi network

**Limitations**:
- Only works on same network
- Your computer must stay on

---

## Troubleshooting

### Backend fails to start on Render
- **Issue**: Out of memory (512MB not enough)
- **Solution**: Upgrade to Railway or Render paid tier ($7/month)

### CORS errors
- **Issue**: Frontend can't connect to backend
- **Solution**: Update `ALLOWED_ORIGINS` in backend environment variables

### Frontend shows "Network Error"
- **Issue**: Wrong API URL
- **Solution**: Check `VITE_API_URL` environment variable

### Processing is very slow
- **Issue**: Free tier resources are limited
- **Solution**: Use ngrok (your local machine) or upgrade to paid tier

---

## Recommendation

For quick testing with your friend:

1. **Fastest**: Use **ngrok** (Option 1) - 2 minutes, works immediately
2. **Most reliable**: Use **Railway.app** (Option 3) - $5 credit, best performance
3. **Completely free**: Use **Render.com** (Option 2) - May be slow but works

I recommend starting with **ngrok** since both servers are already running on your machine!
