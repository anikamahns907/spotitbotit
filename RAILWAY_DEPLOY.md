# Deploy to Railway - Step by Step Guide

Railway provides a free tier and is the easiest way to get a permanent public URL for your game!

## Method 1: Using Railway Web Interface (Easiest - No CLI needed)

### Step 1: Prepare Your Code
✅ All files are already set up! You have:
- `requirements.txt` - Dependencies
- `Procfile` - Tells Railway how to run your app
- `main.py` - Your FastAPI server (already configured for cloud)

### Step 2: Push to GitHub
1. Create a new repository on GitHub (if you haven't already)
2. Push your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

### Step 3: Deploy on Railway
1. **Go to:** https://railway.app
2. **Sign up** (free) - Use GitHub to sign in
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your repository** (spotitbotit)
6. **Railway will automatically:**
   - Detect it's a Python app
   - Install dependencies from `requirements.txt`
   - Run your app using the `Procfile`
7. **Wait for deployment** (~2-3 minutes)
8. **Get your URL:** Railway will give you a URL like `https://your-app.railway.app`
9. **Share that URL** with your friend! 🎉

### Step 4: (Optional) Custom Domain
- Railway gives you a free `.railway.app` domain
- You can add a custom domain in Railway settings if you want

---

## Method 2: Using Railway CLI (For Developers)

### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

### Step 2: Login
```bash
railway login
```

### Step 3: Initialize & Deploy
```bash
cd /Users/anikamahns/Documents/GitHub/spotitbotit
railway init
railway up
```

### Step 4: Get Your URL
```bash
railway domain
```

---

## Troubleshooting

### If deployment fails:
1. Check Railway logs in the dashboard
2. Make sure `requirements.txt` has all dependencies
3. Verify `Procfile` exists and has: `web: python main.py`

### If WebSocket doesn't work:
- Railway supports WebSockets by default
- Make sure you're using `wss://` (secure WebSocket) in production
- The frontend code should automatically detect HTTPS and use WSS

### Port Configuration:
- Railway automatically sets the `PORT` environment variable
- Your `main.py` already reads this: `port = int(os.environ.get("PORT", 8000))`
- No changes needed! ✅

---

## After Deployment

1. **Test your URL:** Open it in a browser
2. **Share with friends:** They can access from anywhere!
3. **Monitor:** Check Railway dashboard for logs and usage

---

## Free Tier Limits

Railway free tier includes:
- ✅ 500 hours/month compute time
- ✅ $5 credit/month
- ✅ Public URL (`.railway.app` domain)
- ✅ Automatic HTTPS
- ✅ WebSocket support

Perfect for personal projects and testing! 🚀

