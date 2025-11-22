# ElevenLabs TTS Setup Guide

## What is ElevenLabs?

ElevenLabs provides AI-powered text-to-speech with very human-like voices. It's much better than browser TTS and sounds like a real person speaking.

## Setup Instructions

### Step 1: Get Your Free API Key

1. Go to https://elevenlabs.io
2. Sign up for a free account (free tier includes 10,000 characters/month)
3. Go to your profile/settings
4. Copy your API key

### Step 2: Add Your API Key

Open `tetris_therapist/templates/game.html` and find the script section at the bottom. Uncomment and add your key:

```javascript
const ELEVENLABS_API_KEY = 'your-actual-api-key-here';
```

Or you can set it directly in `tetris_therapist/static/js/tetris.js` at the top:

```javascript
let ELEVENLABS_API_KEY = 'your-actual-api-key-here';
```

### Step 3: Choose a Voice

The default voice is **Adam** - a deep British male voice perfect for a therapist.

Other good British male voices:
- **Arnold** (Voice ID: `VR6AewLTigWG4xSOukaG`) - British male
- **Adam** (Voice ID: `pNInz6obpgDQGcFmaJgB`) - Deep British male (default)

To change the voice, edit `ELEVENLABS_VOICE_ID` in `tetris_therapist/static/js/tetris.js`

### Step 4: Test It

1. Start the Django server
2. Play the game
3. When Dr. Tetris speaks, you should hear a human-like British male voice

## How It Works

- If you have an ElevenLabs API key set, it will use ElevenLabs for human-like speech
- If no API key is set, it falls back to browser TTS (your system voices)
- The voice automatically syncs with the speech bubble animation

## Free Tier Limits

- 10,000 characters per month (free)
- Perfect for testing and small projects
- Upgrade if you need more

## Troubleshooting

- **No voice?** Check browser console for errors
- **Still using browser TTS?** Make sure your API key is set correctly
- **API errors?** Check your ElevenLabs dashboard for usage/quota

