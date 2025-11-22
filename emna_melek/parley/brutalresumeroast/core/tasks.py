"""
Celery tasks for processing resumes and generating roasts
"""
from celery import shared_task
from django.conf import settings
from .models import RoastResult
from .utils import pdf_to_text, build_brutal_prompt, detect_web3_content
import os
import random
import requests


def process_roast(task_id, pdf_path):
    """
    Core roast processing logic (can be called directly or via Celery)
    """
    result = RoastResult.objects.get(task_id=task_id)
    result.status = 'processing'
    result.save()
    
    try:
        # Extract text from PDF
        resume_text = pdf_to_text(pdf_path)
        
        if not resume_text or len(resume_text.strip()) < 50:
            raise Exception("Resume text too short or empty")
        
        # Build prompt
        prompt = build_brutal_prompt(resume_text)
        
        # Call Groq API
        roast_text = call_groq_api(prompt)
        
        # Optional: Generate image if HF API key is set
        image_url = None
        if settings.HF_API_KEY:
            try:
                image_url = generate_hell_image(resume_text)
            except:
                pass  # Image generation is optional
        
        # Save result
        result.roast_text = roast_text
        result.image_url = image_url
        result.mark_completed()
        
        return roast_text
        
    except Exception as e:
        result.status = 'failed'
        result.roast_text = f"Error: {str(e)}"
        result.save()
        raise


@shared_task(bind=True, max_retries=3)
def roast_resume_task(self, task_id, pdf_path):
    """
    Celery task wrapper - calls process_roast()
    """
    return process_roast(task_id, pdf_path)


def call_groq_api(prompt):
    """
    Call Groq API to generate roast.
    Uses free models: llama-3.1-70b-versatile or mixtral-8x22b-instruct
    """
    if not settings.GROQ_API_KEY:
        # Fallback to example roast if no API key
        return get_fallback_roast()
    
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": settings.GROQ_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a brutally honest, toxic senior engineer from Levels.fyi. Be savage, hilarious, and use 2022-2025 memes. Never be constructive."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.9,
            "max_tokens": 2000,
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        roast_text = data['choices'][0]['message']['content']
        
        return roast_text
        
    except Exception as e:
        # Fallback to example roast on error
        print(f"Groq API error: {e}")
        return get_fallback_roast()


def generate_hell_image(resume_text):
    """
    Optional: Generate a "resume burning in hell" image using Hugging Face.
    """
    if not settings.HF_API_KEY:
        return None
    
    try:
        # Using a text-to-image model (example with stable-diffusion)
        # This is optional and may require specific model access
        url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}
        
        prompt = "a resume document burning in hellfire, dramatic lighting, dark background, professional photo on fire"
        
        response = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=30)
        
        if response.status_code == 200:
            # Save image and return URL
            # For now, return None as this requires file handling
            return None
        else:
            return None
    except:
        return None


def get_fallback_roasts():
    """
    Return all pre-written brutal roasts for RAG retrieval.
    """
    return [
        """🔥 ONE-LINER: Your resume just got ratio'd by a LinkedIn recruiter bot.

• "5 years of experience" but your GitHub has 3 commits from 2019. Sure, Jan.
• You listed "Microsoft Office" as a skill. In 2025. I'm calling the police.
• "Fast learner" = "I don't know anything but I'll Google it during standup"
• Your "passion for technology" is showing... in your 2018 Bootstrap portfolio
• "Team player" but your references are your mom and your cat
• You put "blockchain" on your resume. Automatic rejection. No appeals.
• "Detail-oriented" but you misspelled your own email address
• Your cover letter starts with "To whom it may concern" in 2025. We're done here.
• "Self-starter" = "I need constant supervision but I'm trying"
• Your resume is 3 pages. You're not a senior engineer, you're writing a novel.
• "Proficient in Python" but you can't explain what a list comprehension is
• You listed "Agile" as a skill. That's not a skill, that's a meeting structure.
• Your GitHub link goes to a 404. Peak performance.
• "Excellent communication skills" but your resume reads like a ransom note
• You put "blockchain" twice. I'm blocking you twice.

Realistic TC: $38k + ramen + "exposure" from your startup founder""",
        
        """💀 ONE-LINER: Your resume has less substance than a Twitter blue checkmark.

• "10+ years of experience" but your tech stack is from 2015. Time to update, grandpa.
• You listed "HTML" as a separate skill. In 2025. We're not in 1999 anymore.
• "Full-stack developer" but your frontend is jQuery and your backend is PHP 5.6
• Your portfolio site uses Comic Sans. I'm not even joking. This is real.
• "Passionate about coding" but your last commit was "fix typo" 6 months ago
• You put "blockchain expertise" on your resume. That's a red flag, not a skill.
• "Strong problem-solving skills" but you can't solve why your code doesn't work
• Your resume has 47 bullet points. I stopped reading at bullet 3.
• "Excellent team player" but you work remotely and never turn on your camera
• You listed "Microsoft Word" as a technical skill. We're done here.
• Your GitHub has 1 repository: "hello-world" from 2018. Impressive.
• "Detail-oriented" but you used Times New Roman. In 2025. On a tech resume.
• You put "blockchain" three times. I'm calling security.
• "Self-taught developer" but you can't explain what async/await does
• Your resume is written in the third person. Are you writing about yourself or someone else?

Realistic TC: $42k + "equity" (worthless stock options) + free coffee""",
        
        """⚡ ONE-LINER: Your resume got rejected by an AI before a human even saw it.

• "5 years of experience" but you're still using var instead of const. JavaScript called, it wants its 2015 syntax back.
• You listed "blockchain" as your top skill. That's not a skill, that's a warning sign.
• "Full-stack developer" but your stack is LAMP from 2010. The stack, not the lamp.
• Your portfolio is a single HTML file with inline CSS. Modern web development called, it's concerned.
• "Passionate about technology" but your last tech blog post was about "Why jQuery is still relevant" in 2023
• You put "Microsoft Excel" as a programming skill. Excel macros don't count, Karen.
• "Strong communication skills" but your resume has 12 different fonts. Pick one. Please.
• Your GitHub profile picture is a default avatar. Even GitHub knows you're not serious.
• "Team player" but your LinkedIn says "Open to work" for 2 years. Teams are avoiding you.
• You listed "blockchain" four times. I'm blocking you four times.
• "Fast learner" but you've been "learning React" for 3 years. At this point, you're a slow learner.
• Your resume has a QR code. To your LinkedIn. Which also has a QR code. QRception.
• "Detail-oriented" but you misspelled "JavaScript" as "Javascript" throughout your resume
• You put "blockchain" in your summary, skills, AND experience. We get it. You like blockchain. We don't.
• Your cover letter mentions "synergy" unironically. This isn't a 2005 corporate retreat.

Realistic TC: $35k + "unlimited PTO" (which means no PTO) + pizza on Fridays"""
    ]


def get_fallback_roast():
    """
    Return a random pre-written brutal roast as fallback.
    """
    fallback_roasts = get_fallback_roasts()
    return random.choice(fallback_roasts)

