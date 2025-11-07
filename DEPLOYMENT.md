# Deployment Guide - Make Your Game Accessible Online

## Option 1: ngrok (Quick & Easy - Best for Testing)

**ngrok** creates a public URL that tunnels to your local server. Perfect for testing!

### Steps:

1. **Install ngrok:**
   ```bash
   # On Mac (using Homebrew):
   brew install ngrok
   
   # Or download from: https://ngrok.com/download
   ```

2. **Start your game server:**
   ```bash
   python main.py
   ```

3. **In a new terminal, start ngrok:**
   ```bash
   ngrok http 8000
   ```

4. **Copy the public URL:**
   - You'll see something like: `https://abc123.ngrok-free.app`
   - Share this URL with your friend!
   - Both players use the same URL

### Notes:
- Free ngrok URLs expire after 2 hours (or restart)
- For permanent URLs, sign up for a free ngrok account
- The URL works from anywhere in the world!

---

## Option 2: Cloud Deployment (Permanent Solution)

Deploy to a cloud service for a permanent URL. Here are the best options:

### A. Railway (Recommended - Free Tier Available)

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and deploy:**
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Get your public URL:**
   - Railway provides a permanent URL like: `https://your-app.railway.app`

### B. Render (Free Tier Available)

1. **Create account at:** https://render.com
2. **Create a new Web Service**
3. **Connect your GitHub repo**
4. **Set build command:** `pip install -r requirements.txt`
5. **Set start command:** `python main.py`
6. **Deploy!**

### C. Fly.io (Free Tier Available)

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Create `fly.toml`:**
   ```toml
   app = "your-app-name"
   primary_region = "iad"

   [build]

   [http_service]
     internal_port = 8000
     force_https = true
     auto_stop_machines = true
     auto_start_machines = true
     min_machines_running = 0
     processes = ["app"]

   [[vm]]
     cpu_kind = "shared"
     cpus = 1
     memory_mb = 256
   ```

3. **Deploy:**
   ```bash
   fly launch
   fly deploy
   ```

### D. PythonAnywhere (Free Tier Available)

1. **Sign up at:** https://www.pythonanywhere.com
2. **Upload your files**
3. **Configure web app**
4. **Set WSGI file to point to your FastAPI app**

---

## Option 3: Update Code for Production

For cloud deployment, you may need to update `main.py`:

```python
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

This allows cloud services to set the port via environment variable.

---

## Quick Comparison

| Method | Setup Time | Cost | Permanent URL | Best For |
|--------|-----------|------|---------------|----------|
| ngrok | 2 min | Free | No (expires) | Testing |
| Railway | 5 min | Free tier | Yes | Quick deploy |
| Render | 10 min | Free tier | Yes | Easy GUI |
| Fly.io | 10 min | Free tier | Yes | Full control |

---

## Recommendation

- **For quick testing:** Use **ngrok**
- **For permanent deployment:** Use **Railway** or **Render** (easiest)

