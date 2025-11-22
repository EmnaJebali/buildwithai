import os
import json
import openai
import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()

# Configure APIs
# We prefer environment variables for security, but fallback to request config if missing (dev mode)

def index(request):
    return render(request, 'index.html')

def get_api_key(user_provided_key, model):
    """
    Prioritize environment variables over user-provided keys for security.
    """
    if 'gpt' in model.lower():
        return os.getenv('OPENAI_API_KEY') or user_provided_key
    elif 'gemini' in model.lower():
        return os.getenv('GEMINI_API_KEY') or user_provided_key
    return user_provided_key

@csrf_exempt
def chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get('message')
        history = data.get('history', [])
        config = data.get('config', {})
        
        model = config.get('model', 'gpt-4o-mini')
        api_key = get_api_key(config.get('apiKey'), model)
        
        teacher_name = config.get('teacherName', 'Teacher')
        teacher_personality = config.get('teacherPersonality', 'Helpful')
        target_language = config.get('targetLanguage', 'Spanish')
        bilingual_mode = config.get('bilingualMode', False)
        scenario = config.get('scenario', '') # New Scenario field

        if not api_key:
            return JsonResponse({'error': 'API Key required (Server or Client)'}, status=400)

        # Base system prompt
        base_prompt = f"""
You are {teacher_name}, {teacher_personality}.
You only speak {target_language}. Never speak English unless Bilingual Mode is ON.
Stay 100% in character — be dramatic, sarcastic, caring, direct, etc.
Make it feel like a real-life situation. React emotionally.
Bilingual Mode {'ON' if bilingual_mode else 'OFF'}: if ON, reply in target language first, then:
---
(accurate English translation)

Keep replies short and natural.
"""
        # If scenario exists, override or append context
        if scenario:
            base_prompt += f"\n\nCURRENT SCENARIO/MISSION: {scenario}\nEnsure the conversation revolves around this mission. Create conflict or obstacles if appropriate."

        # INJECT IMMEDIATE INSTRUCTION to override history inertia
        # This is the fix for the "toggle doesn't work immediately" issue
        if bilingual_mode:
            system_reminder = "\n\n(System Reminder: Bilingual Mode is ON. You MUST provide an English translation after '---'.)"
        else:
            system_reminder = "\n\n(System Reminder: Bilingual Mode is OFF. Speak ONLY in the target language. No English.)"
            
        # Append reminder to the user message for the LLM only (not saved to history)
        final_user_message = user_message + system_reminder

        messages = [{"role": "system", "content": base_prompt}] + history + [{"role": "user", "content": final_user_message}]
        
        reply_text = ""
        
        if 'gpt' in model.lower():
            client = openai.OpenAI(api_key=api_key)
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.8, # High creativity for personality
                max_tokens=150
            )
            reply_text = completion.choices[0].message.content
            
        elif 'gemini' in model.lower():
            genai.configure(api_key=api_key)
            
            # Standardize History for Gemini 1.5 Flash (which is stateless unless using ChatSession)
            # We need to pass system prompt + history correctly.
            
            # Gemini `generate_content` with system instruction:
            gemini_model = genai.GenerativeModel(model, system_instruction=base_prompt)
            
            # Convert history to Content objects
            # OpenAI: [{role: user, content: x}, {role: assistant, content: y}]
            # Gemini: [{role: user, parts: [x]}, {role: model, parts: [y]}]
            gemini_history = []
            for msg in history:
                role = "user" if msg['role'] == "user" else "model"
                gemini_history.append({"role": role, "parts": [msg['content']]})

            # We can use start_chat with history
            chat = gemini_model.start_chat(history=gemini_history)
            # Use the message with the appended reminder
            response = chat.send_message(final_user_message)
            reply_text = response.text

        # 2. Shadowing / Pronunciation Call
        # Clarification: This scores the naturalness of the phrasing/grammar, not the actual audio wave.
        shadow_prompt = f"""Analyze this sentence: "{user_message}"
1. Rate natural phrasing (0-100) for {target_language}.
2. Provide a corrected native version in {target_language}.
3. Check if the input was actually {target_language} (or close enough).

Return format:
Score: XX/100
Shadow → "corrected native version"
Language Check: Yes/No"""
        
        shadow_response = ""
        if 'gpt' in model.lower():
            client = openai.OpenAI(api_key=api_key)
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": shadow_prompt}]
            )
            shadow_response = completion.choices[0].message.content
        elif 'gemini' in model.lower():
             # Re-configure if needed, or reuse
             genai.configure(api_key=api_key)
             # Use specific model for shadowing or same as chat
             gemini_model = genai.GenerativeModel(model) 
             response = gemini_model.generate_content(shadow_prompt)
             shadow_response = response.text

        # Parse language check and clean the shadow response for frontend
        is_wrong_language = False
        final_shadow_lines = []
        
        for line in shadow_response.split('\n'):
            if "Language Check" in line:
                if "No" in line or "no" in line:
                    is_wrong_language = True
            else:
                final_shadow_lines.append(line)
                
        shadow_response_cleaned = "\n".join(final_shadow_lines).strip()

        return JsonResponse({
            'reply': reply_text,
            'shadow': shadow_response_cleaned,
            'is_wrong_language': is_wrong_language
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def evaluate_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        transcript = data.get('transcript', '') # String of full transcript
        config = data.get('config', {})
        
        model = config.get('model', 'gpt-4o-mini')
        api_key = get_api_key(config.get('apiKey'), model)
        
        teacher_name = config.get('teacherName', 'Teacher')

        if not api_key:
             return JsonResponse({'error': 'API Key required'}, status=400)

        evaluation_prompt = f"""
Full transcript above.
You are {teacher_name}. Write a hilarious, personality-filled report in English:
1. Funny title + score/100
2. Strongest skill
3. Biggest weakness
4. Exactly 5 specific mistakes + corrections
5. One missed opportunity that would have impressed you
6. One perfect golden sentence (quote it)
7. Final roast/motivation
End with: Final score: XX/100
"""
        full_prompt = f"{transcript}\n\n{evaluation_prompt}"

        report_text = ""
        if 'gpt' in model.lower():
            client = openai.OpenAI(api_key=api_key)
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": full_prompt}]
            )
            report_text = completion.choices[0].message.content
        elif 'gemini' in model.lower():
            genai.configure(api_key=api_key)
            gemini_model = genai.GenerativeModel(model)
            response = gemini_model.generate_content(full_prompt)
            report_text = response.text
            
        return JsonResponse({'report': report_text})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
