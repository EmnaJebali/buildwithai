# 🚀 Quick Start Guide

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Set Up Environment

Copy the example env file:
```bash
cp brutalresumeroast/env.example brutalresumeroast/.env
```

Edit `.env` and add your Groq API key:
```
GROQ_API_KEY=your-actual-api-key-here
```

Get free API key at: https://console.groq.com

## 3. Start Redis

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**Windows:**
Download from: https://github.com/microsoftarchive/redis/releases

## 4. Run Migrations

```bash
python manage.py migrate
```

## 5. Start Celery Worker (Terminal 1)

```bash
celery -A brutalresumeroast worker --loglevel=info
```

## 6. Start Django Server (Terminal 2)

```bash
python manage.py runserver
```

## 7. Visit

Open http://localhost:8000 and upload a PDF!

---

## 🎯 Testing Without Groq API

If you don't have a Groq API key yet, the app will automatically use fallback roasts (pre-written hilarious roasts). Perfect for testing!

## 📝 Adding Example PDFs (Optional)

To add pre-roasted example PDFs for demo fallback:

1. Place 3 PDF files in `media/examples/`
2. Name them: `example1.pdf`, `example2.pdf`, `example3.pdf`
3. The app will use these if Celery fails

---

**That's it! You're ready to roast resumes! 🔥**

