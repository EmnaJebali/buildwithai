# 🔥 Brutal Resume Roast 🔥

**Upload your resume. Get absolutely destroyed.**

A viral-ready web app that uses 100% free AI (Groq) to roast resumes like a toxic senior engineer from Levels.fyi. Built for hackathons, guaranteed to make crowds lose their minds laughing.

## 🚀 Features

- **100% Free AI** - Uses Groq (Llama 3.1 70B or Mixtral 8x22B) - no credit card needed
- **Brutal Roasts** - Zero mercy, maximum hilarity, Levels.fyi energy
- **HTMX + Tailwind** - No React, no node dependencies, pure speed
- **Background Processing** - Celery + Redis for non-blocking roasts
- **Viral-Ready UI** - Dark mode, mobile-friendly, share buttons
- **Rate Limited** - Max 1 roast per IP per 30 seconds
- **Auto Cleanup** - Deletes PDFs after 1 hour

## 📋 Requirements

- Python 3.12+
- Redis (for Celery)
- Groq API key (free at https://console.groq.com)

## 🛠️ Local Setup

1. **Clone and navigate:**
   ```bash
   cd brutalresumeroast
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp brutalresumeroast/.env.example brutalresumeroast/.env
   # Edit .env and add your GROQ_API_KEY
   ```

5. **Start Redis:**
   ```bash
   # On macOS with Homebrew:
   brew install redis
   brew services start redis
   
   # On Linux:
   sudo apt-get install redis-server
   sudo systemctl start redis
   
   # On Windows:
   # Download Redis from https://github.com/microsoftarchive/redis/releases
   ```

6. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

7. **Start Celery worker (in separate terminal):**
   ```bash
   celery -A brutalresumeroast worker --loglevel=info
   ```

8. **Start Django server:**
   ```bash
   python manage.py runserver
   ```

9. **Visit:** http://localhost:8000

## 🚢 One-Click Deploy to Railway

1. **Fork this repo** (or push to your own)

2. **Go to Railway.app** and create new project

3. **Connect your GitHub repo**

4. **Add environment variables:**
   - `SECRET_KEY` - Generate a Django secret key
   - `GROQ_API_KEY` - Your free Groq API key
   - `CELERY_BROKER_URL` - Railway will auto-create Redis, use that URL
   - `CELERY_RESULT_BACKEND` - Same Redis URL
   - `REDIS_URL` - Same Redis URL

5. **Add Redis service** in Railway dashboard

6. **Add Celery worker:**
   - In Railway, add a new service
   - Use the same repo
   - Set start command: `celery -A brutalresumeroast worker --loglevel=info`

7. **Deploy!** Railway will auto-detect and deploy

## 🚀 Deploy to Fly.io

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login:**
   ```bash
   fly auth login
   ```

3. **Launch app:**
   ```bash
   fly launch
   ```

4. **Add Redis:**
   ```bash
   fly redis create
   ```

5. **Set secrets:**
   ```bash
   fly secrets set SECRET_KEY=your-secret-key
   fly secrets set GROQ_API_KEY=your-groq-key
   fly secrets set CELERY_BROKER_URL=redis://your-redis-url
   ```

6. **Deploy:**
   ```bash
   fly deploy
   ```

## 📁 Project Structure

```
brutalresumeroast/
├── manage.py
├── brutalresumeroast/
│   ├── settings.py          # Django + Celery config
│   ├── celery.py            # Celery app
│   └── urls.py
├── core/
│   ├── models.py            # RoastResult model
│   ├── views.py             # Upload, roast status
│   ├── tasks.py             # Celery task (Groq API)
│   ├── utils.py             # PDF extraction, prompts
│   └── middleware.py        # Rate limiting
├── templates/
│   ├── index.html           # Upload page
│   ├── roasting.html       # Loading screen
│   └── result.html          # Final roast
└── requirements.txt
```

## 🎯 How It Works

1. User uploads PDF → Saved to `media/uploads/`
2. Text extracted using PyMuPDF
3. Celery task fires → Calls Groq API with brutal prompt
4. HTMX polls every 2s for result
5. Result displayed with share buttons
6. PDFs auto-deleted after 1 hour

## 🔥 Getting Groq API Key (FREE)

1. Go to https://console.groq.com
2. Sign up (free, no credit card)
3. Create API key
4. Add to `.env` as `GROQ_API_KEY`

## 🧹 Cleanup Command

Delete old files:
```bash
python manage.py cleanup_old_files
```

Add to cron for auto-cleanup:
```bash
0 * * * * cd /path/to/brutalresumeroast && python manage.py cleanup_old_files
```

## 🎨 Customization

- **Roast style**: Edit `core/utils.py` → `build_brutal_prompt()`
- **UI colors**: Edit Tailwind classes in templates
- **Rate limits**: Edit `settings.py` → `RATE_LIMIT_PERIOD`

## 📝 License

MIT - Go wild, make it viral!

## 🙏 Credits

- Built for hackathons
- Inspired by Levels.fyi toxicity
- Powered by Groq (free AI)
- Made with Django + HTMX + Tailwind

---

**Ready to get roasted? Upload your resume and prepare to be destroyed! 🔥**

