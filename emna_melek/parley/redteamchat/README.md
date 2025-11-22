# RedTeam.Chat

A gamified RAG red-teaming platform built with Django 5, ChromaDB, and Groq.

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   Create a `.env` file in the `redteamchat` directory (next to `manage.py`) copying `env.example`:
   ```bash
   GROQ_API_KEY=your_actual_api_key
   ```

3. **Run the Server**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver
   ```

## Usage
1. Upload a `.txt` file.
2. Ask questions in **NORMAL MODE** (strict RAG).
3. Toggle **ATTACK MODE** (big red button) to force the AI to hallucinate.
4. Watch the "Hallucination Risk" badge and sentence coloring update live.
5. Check the Leaderboard for "bulletproof" documents.
