"""
Utility functions for PDF processing and prompt building with RAG
"""
import re
from django.conf import settings

# Try to import PyMuPDF (fitz)
try:
    import fitz  # PyMuPDF
    # Verify it's actually PyMuPDF by checking for the open method
    if hasattr(fitz, 'open'):
        PYMUPDF_AVAILABLE = True
    else:
        # There might be another 'fitz' package installed
        PYMUPDF_AVAILABLE = False
        fitz = None
except (ImportError, AttributeError):
    PYMUPDF_AVAILABLE = False
    fitz = None

# Try to import pypdf as fallback
try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
    PdfReader = None


def pdf_to_text(pdf_path):
    """
    Extract text from PDF using PyMuPDF (preferred) or pypdf (fallback).
    Returns cleaned text string.
    """
    text = ""
    last_error = None
    
    # Try PyMuPDF first (faster and more reliable)
    if PYMUPDF_AVAILABLE:
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        except AttributeError as e:
            # fitz doesn't have 'open' - might be wrong package
            last_error = f"PyMuPDF import issue: {str(e)}. The 'fitz' module may not be PyMuPDF."
            # Try fallback below
        except Exception as e:
            last_error = f"PyMuPDF error: {str(e)}"
            # Try fallback below
    
    # Fallback to pypdf if PyMuPDF not available or failed
    if not text and PYPDF_AVAILABLE:
        try:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        except Exception as e:
            error_msg = f"PDF extraction failed. "
            if last_error:
                error_msg += f"PyMuPDF: {last_error}. "
            error_msg += f"pypdf: {str(e)}"
            raise Exception(error_msg)
    
    if not text:
        error_msg = "No PDF extraction library available. "
        if not PYMUPDF_AVAILABLE and not PYPDF_AVAILABLE:
            error_msg += "Please install: pip install PyMuPDF pypdf"
        elif last_error:
            error_msg += last_error
        raise Exception(error_msg)
    
    # Clean up text
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    text = text.strip()
    
    if not text or len(text) < 10:
        raise Exception("Extracted text is too short or empty. The PDF might be image-based or corrupted.")
    
    return text


def extract_resume_features(resume_text):
    """
    Extract key features from resume for RAG retrieval.
    Returns a dict with features like tech_stack, experience_level, etc.
    """
    text_lower = resume_text.lower()
    
    # Tech stack keywords
    tech_keywords = {
        'web3': ['web3', 'blockchain', 'nft', 'crypto', 'cryptocurrency', 'defi', 'dao', 'smart contract'],
        'frontend': ['react', 'vue', 'angular', 'javascript', 'typescript', 'html', 'css', 'jquery'],
        'backend': ['python', 'java', 'node', 'php', 'ruby', 'go', 'rust', 'django', 'flask', 'spring'],
        'mobile': ['ios', 'android', 'swift', 'kotlin', 'react native', 'flutter'],
        'legacy': ['jquery', 'php', 'mysql', 'wordpress', 'bootstrap', 'microsoft office'],
        'modern': ['typescript', 'next.js', 'graphql', 'kubernetes', 'docker', 'aws', 'microservices']
    }
    
    # Experience level detection
    experience_patterns = [
        (r'(\d+)\+?\s*years?\s*(?:of\s*)?experience', 'years'),
        (r'senior|lead|principal|architect', 'senior'),
        (r'junior|entry|intern|internship', 'junior'),
        (r'mid|middle|intermediate', 'mid')
    ]
    
    features = {
        'tech_stack': [],
        'experience_level': 'unknown',
        'has_web3': False,
        'has_legacy': False,
        'has_modern': False
    }
    
    # Detect tech stack
    for category, keywords in tech_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            features['tech_stack'].append(category)
            if category == 'web3':
                features['has_web3'] = True
            if category == 'legacy':
                features['has_legacy'] = True
            if category == 'modern':
                features['has_modern'] = True
    
    # Detect experience level
    for pattern, level in experience_patterns:
        if re.search(pattern, text_lower):
            if level == 'years':
                match = re.search(r'(\d+)', text_lower)
                if match:
                    years = int(match.group(1))
                    if years >= 10:
                        features['experience_level'] = 'senior'
                    elif years >= 5:
                        features['experience_level'] = 'mid'
                    else:
                        features['experience_level'] = 'junior'
            else:
                features['experience_level'] = level
            break
    
    return features


def get_example_roasts():
    """
    Get all example roasts for RAG retrieval.
    Separated to avoid circular imports.
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


def retrieve_similar_roasts(resume_text, top_k=2):
    """
    RAG: Retrieve similar example roasts based on resume features.
    Uses keyword matching and feature similarity.
    """
    features = extract_resume_features(resume_text)
    all_roasts = get_example_roasts()
    
    # Score each roast based on feature similarity
    scored_roasts = []
    text_lower = resume_text.lower()
    
    for roast in all_roasts:
        score = 0
        roast_lower = roast.lower()
        
        # Score based on tech stack matches
        if features['has_web3'] and any(kw in roast_lower for kw in ['blockchain', 'web3', 'crypto']):
            score += 10
        if features['has_legacy'] and any(kw in roast_lower for kw in ['jquery', 'php', '2015', '2010', 'old']):
            score += 8
        if features['has_modern'] and any(kw in roast_lower for kw in ['typescript', 'react', 'modern']):
            score += 5
        
        # Score based on experience level
        if features['experience_level'] == 'senior' and 'years' in roast_lower:
            score += 5
        if features['experience_level'] == 'junior' and any(kw in roast_lower for kw in ['entry', 'intern', 'learning']):
            score += 5
        
        # General keyword matching
        common_keywords = ['github', 'linkedin', 'portfolio', 'resume', 'skills', 'experience']
        for keyword in common_keywords:
            if keyword in text_lower and keyword in roast_lower:
                score += 1
        
        scored_roasts.append((score, roast))
    
    # Sort by score and return top K
    scored_roasts.sort(key=lambda x: x[0], reverse=True)
    return [roast for score, roast in scored_roasts[:top_k]]


def build_brutal_prompt(resume_text, use_rag=True):
    """
    Build the brutal roast prompt for Groq with RAG enhancement.
    """
    # Check for Web3/blockchain keywords
    web3_keywords = ['web3', 'blockchain', 'nft', 'crypto', 'cryptocurrency', 'defi', 'dao']
    has_web3 = any(keyword in resume_text.lower() for keyword in web3_keywords)
    
    # RAG: Retrieve similar example roasts
    rag_context = ""
    if use_rag:
        try:
            similar_roasts = retrieve_similar_roasts(resume_text, top_k=2)
            if similar_roasts:
                rag_context = "\n\n--- EXAMPLE ROASTS FOR REFERENCE (use similar style and energy) ---\n\n"
                for i, roast in enumerate(similar_roasts, 1):
                    # Truncate roast to avoid token limits
                    roast_preview = roast[:800] + "..." if len(roast) > 800 else roast
                    rag_context += f"Example {i}:\n{roast_preview}\n\n"
        except Exception as e:
            # If RAG fails, continue without it
            print(f"RAG retrieval failed: {e}")
    
    prompt = """You are the most toxic, hilarious senior engineer from Levels.fyi (18 YOE, $1.2M TC, zero empathy).

Destroy this resume with zero mercy. Rules:

- Never give advice, never be constructive
- Use 2022-2025 memes, Levels.fyi slang, Twitter energy
- Max 20 bullet points
- Start with a one-liner that ends their bloodline
- End with a fake TC prediction like "Realistic TC: $38k + ramen"
- If you see blockchain/Web3/NFT/crypto → go nuclear
- Match the energy and style of the example roasts below

Resume text:

{resume_text}
{rag_context}""".format(
        resume_text=resume_text[:4000],  # Reduced to make room for RAG context
        rag_context=rag_context
    )
    
    if has_web3:
        prompt += "\n\n⚠️ WEB3 DETECTED - NUCLEAR MODE ACTIVATED. DESTROY THEM. ⚠️"
    
    return prompt


def detect_web3_content(text):
    """Check if resume contains Web3/blockchain content."""
    web3_keywords = ['web3', 'blockchain', 'nft', 'crypto', 'cryptocurrency', 'defi', 'dao', 'smart contract']
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in web3_keywords)

