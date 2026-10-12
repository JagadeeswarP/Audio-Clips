import re
import os
import asyncio
import edge_tts
import requests

VOICE_OPTIONS = {
    "en-US-GuyNeural": {
        "name": "Guy",
        "description": "Deep, warm baritone American male voice (ideal for storytelling & documentaries)",
        "gender": "Male",
        "locale": "en-US",
    },
    "en-US-ChristopherNeural": {
        "name": "Christopher",
        "description": "Cinematic, deep narrative baritone male voice",
        "gender": "Male",
        "locale": "en-US",
    },
    "en-US-EricNeural": {
        "name": "Eric",
        "description": "Engaging, conversational American male voice (ideal for Shorts & TikTok)",
        "gender": "Male",
        "locale": "en-US",
    },
    "en-US-JennyNeural": {
        "name": "Jenny",
        "description": "Clear, natural, professional American female voice",
        "gender": "Female",
        "locale": "en-US",
    },
    "en-US-AriaNeural": {
        "name": "Aria",
        "description": "Expressive, engaging American female voice",
        "gender": "Female",
        "locale": "en-US",
    },
    "en-US-AvaNeural": {
        "name": "Ava",
        "description": "Thoughtful, modern American female voice",
        "gender": "Female",
        "locale": "en-US",
    },
    "en-US-AndrewNeural": {
        "name": "Andrew",
        "description": "Warm, authentic American male voice",
        "gender": "Male",
        "locale": "en-US",
    },
    "en-US-BrianNeural": {
        "name": "Brian",
        "description": "Relaxed, confident American male voice with an easy conversational cadence",
        "gender": "Male",
        "locale": "en-US",
    },
    "en-US-DavisNeural": {
        "name": "Davis",
        "description": "Polished, steady American male voice for explainers and business content",
        "gender": "Male",
        "locale": "en-US",
    },
    "en-US-JacobNeural": {
        "name": "Jacob",
        "description": "Youthful, friendly American male voice for approachable creator videos",
        "gender": "Male",
        "locale": "en-US",
    },
    "en-US-RogerNeural": {
        "name": "Roger",
        "description": "Mature, reassuring American male voice with a measured delivery",
        "gender": "Male",
        "locale": "en-US",
    },
    "en-US-SteffanNeural": {
        "name": "Steffan",
        "description": "Clear, dependable American male voice for tutorials and narration",
        "gender": "Male",
        "locale": "en-US",
    },
    "en-US-TonyNeural": {
        "name": "Tony",
        "description": "Lively, expressive American male voice for energetic social content",
        "gender": "Male",
        "locale": "en-US",
    },
    "en-US-AmberNeural": {
        "name": "Amber",
        "description": "Warm, natural American female voice with a calm, relatable tone",
        "gender": "Female",
        "locale": "en-US",
    },
    "en-US-AnaNeural": {
        "name": "Ana",
        "description": "Bright, friendly American female voice for upbeat creator narration",
        "gender": "Female",
        "locale": "en-US",
    },
    "en-US-AshleyNeural": {
        "name": "Ashley",
        "description": "Confident, conversational American female voice for lifestyle and explainers",
        "gender": "Female",
        "locale": "en-US",
    },
    "en-US-CoraNeural": {
        "name": "Cora",
        "description": "Smooth, thoughtful American female voice for reflective storytelling",
        "gender": "Female",
        "locale": "en-US",
    },
    "en-US-ElizabethNeural": {
        "name": "Elizabeth",
        "description": "Refined, expressive American female voice for premium narration",
        "gender": "Female",
        "locale": "en-US",
    },
    "en-US-EmmaNeural": {
        "name": "Emma",
        "description": "Friendly, clear American female voice with an inviting natural flow",
        "gender": "Female",
        "locale": "en-US",
    },
    "en-US-MichelleNeural": {
        "name": "Michelle",
        "description": "Professional, composed American female voice for educational content",
        "gender": "Female",
        "locale": "en-US",
    },
    "en-US-MonicaNeural": {
        "name": "Monica",
        "description": "Empathetic, articulate American female voice for advice and wellness videos",
        "gender": "Female",
        "locale": "en-US",
    },
}

# Default voice presets for US Content Creators (YouTube Shorts, Reels, Podcasts, Documentaries)
VOICE_PRESETS = {
    "deep_narrator": {
        "name": "Deep Baritone Narrator",
        "description": "Grounded, warm American male baritone with smooth cadence for rich story narration.",
        "voice": "en-US-GuyNeural",
        "pitch": "-4Hz",
        "rate": "+4%",
        "volume": "+0%",
        "pause_comma_ms": 160,
        "pause_period_ms": 400,
        "pause_paragraph_ms": 700,
    },
    "cinematic_thriller": {
        "name": "Cinematic Thriller",
        "description": "Deep dramatic tone with slow, suspenseful pacing for mystery and thriller content.",
        "voice": "en-US-ChristopherNeural",
        "pitch": "-6Hz",
        "rate": "-2%",
        "volume": "+0%",
        "pause_comma_ms": 220,
        "pause_period_ms": 520,
        "pause_paragraph_ms": 900,
    },
    "conversational_creator": {
        "name": "Conversational Creator",
        "description": "Energetic, authentic human voice delivery built for YouTube Shorts, Reels, & TikTok.",
        "voice": "en-US-EricNeural",
        "pitch": "+0Hz",
        "rate": "+6%",
        "volume": "+0%",
        "pause_comma_ms": 140,
        "pause_period_ms": 350,
        "pause_paragraph_ms": 650,
    },
    "documentary_female": {
        "name": "Articulate Documentary Female",
        "description": "Smooth, intelligent, authoritative female delivery for science, nature, and history.",
        "voice": "en-US-JennyNeural",
        "pitch": "+0Hz",
        "rate": "+2%",
        "volume": "+0%",
        "pause_comma_ms": 170,
        "pause_period_ms": 420,
        "pause_paragraph_ms": 780,
    },
    "psychology_insights": {
        "name": "Psychology & Life Insights",
        "description": "Thoughtful, empathetic cadence with subtle emphasis for viral psychology facts and insights.",
        "voice": "en-US-AriaNeural",
        "pitch": "-2Hz",
        "rate": "+4%",
        "volume": "+0%",
        "pause_comma_ms": 180,
        "pause_period_ms": 450,
        "pause_paragraph_ms": 800,
    },
    "friendly_explainer": {
        "name": "Friendly Explainer",
        "description": "Relaxed, personable delivery for explainers, how-tos, and educational Shorts.",
        "voice": "en-US-BrianNeural",
        "pitch": "-1Hz",
        "rate": "+3%",
        "volume": "+0%",
        "pause_comma_ms": 155,
        "pause_period_ms": 390,
        "pause_paragraph_ms": 720,
    },
    "warm_storyteller": {
        "name": "Warm Storyteller",
        "description": "Smooth, reflective female narration with room for emotion and detail.",
        "voice": "en-US-CoraNeural",
        "pitch": "-1Hz",
        "rate": "-1%",
        "volume": "+0%",
        "pause_comma_ms": 190,
        "pause_period_ms": 480,
        "pause_paragraph_ms": 850,
    },
    "upbeat_host": {
        "name": "Upbeat Social Host",
        "description": "Bright, engaging delivery for lifestyle clips, listicles, and social videos.",
        "voice": "en-US-AnaNeural",
        "pitch": "+1Hz",
        "rate": "+8%",
        "volume": "+0%",
        "pause_comma_ms": 125,
        "pause_period_ms": 320,
        "pause_paragraph_ms": 600,
    },
    "calm_authority": {
        "name": "Calm Authority",
        "description": "Measured, reassuring male delivery for financial, technical, and educational topics.",
        "voice": "en-US-RogerNeural",
        "pitch": "-2Hz",
        "rate": "-2%",
        "volume": "+0%",
        "pause_comma_ms": 190,
        "pause_period_ms": 470,
        "pause_paragraph_ms": 820,
    }
}


def preprocess_english_text(text: str, pause_comma_ms: int = 160, pause_period_ms: int = 400, pause_paragraph_ms: int = 700) -> str:
    """
    Cleans up English script text and converts natural punctuation into SSML break tags
    or structured pause markers for natural breathing room and non-robotic flow.
    """
    if not text:
        return ""

    # Normalize whitespace & remove redundant spaces
    cleaned = re.sub(r'[ \t]+', ' ', text).strip()
    
    # Standardize ellipses to clean pause markers
    cleaned = re.sub(r'\.{3,}', '...', cleaned)
    
    # Replace paragraph breaks with SSML breaks
    paragraphs = cleaned.split('\n\n')
    processed_paragraphs = []

    for para in paragraphs:
        lines = para.strip().split('\n')
        processed_lines = []
        for line in lines:
            # Handle ellipses
            line_str = line.replace("...", f' <break time="{int(pause_period_ms * 1.2)}ms"/> ')
            # Add break for periods, exclamations, question marks
            line_str = re.sub(r'([\.!\?])', r'\1 <break time="' + str(pause_period_ms) + 'ms"/> ', line_str)
            # Add break for commas and semicolons
            line_str = re.sub(r'([,;])', r'\1 <break time="' + str(pause_comma_ms) + 'ms"/> ', line_str)
            # Add break for colons, dashes, em-dashes
            line_str = re.sub(r'([:\–\—]|\s--\s)', r'\1 <break time="' + str(int(pause_period_ms * 0.75)) + 'ms"/> ', line_str)
            processed_lines.append(line_str)
        
        para_text = " ".join(processed_lines)
        processed_paragraphs.append(para_text)

    full_ssml_content = f' <break time="{pause_paragraph_ms}ms"/> '.join(processed_paragraphs)
    # Clean up double break spaces
    full_ssml_content = re.sub(r'\s+', ' ', full_ssml_content)
    return full_ssml_content


def text_to_ssml(
    text: str,
    voice: str = "en-US-GuyNeural",
    pitch: str = "-4Hz",
    rate: str = "+4%",
    volume: str = "+0%",
    pause_comma_ms: int = 160,
    pause_period_ms: int = 400
) -> str:
    """
    Wraps text into complete W3C SSML specification for Edge-TTS / Azure Speech.
    """
    ssml_body = preprocess_english_text(text, pause_comma_ms, pause_period_ms)
    
    ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
    <voice name="{voice}">
        <prosody pitch="{pitch}" rate="{rate}" volume="{volume}">
            {ssml_body}
        </prosody>
    </voice>
</speak>"""
    return ssml


def prepare_tts_text(text: str) -> str:
    """
    Keeps synthesis input as clean plain text. edge-tts accepts rate, pitch, and
    volume parameters natively.
    """
    return re.sub(r'[ \t]+', ' ', text).strip()


async def generate_speech_edge(
    text: str,
    output_filepath: str,
    voice: str = "en-US-GuyNeural",
    pitch: str = "-4Hz",
    rate: str = "+4%",
    volume: str = "+0%",
    pause_comma_ms: int = 160,
    pause_period_ms: int = 400
) -> str:
    """
    Synthesizes speech using Microsoft Edge Neural TTS with pitch/rate/pause adjustments.
    """
    if voice not in VOICE_OPTIONS:
        voice = "en-US-GuyNeural"

    tts_text = prepare_tts_text(text)

    communicate = edge_tts.Communicate(
        text=tts_text,
        voice=voice,
        rate=rate,
        pitch=pitch,
        volume=volume
    )
    
    # Save output to specified file
    await communicate.save(output_filepath)
    return output_filepath


def generate_speech_elevenlabs(
    text: str,
    output_filepath: str,
    api_key: str,
    voice_id: str = "pNInz6obpgDQGcFmaJgB", # Default ElevenLabs US Male voice (Adam)
    stability: float = 0.45,
    similarity_boost: float = 0.80,
    style: float = 0.15
) -> str:
    """
    Optional ElevenLabs API integration for high-fidelity US natural voice synthesis.
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": True
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        with open(output_filepath, 'wb') as f:
            f.write(response.content)
        return output_filepath
    else:
        raise Exception(f"ElevenLabs API Error: {response.status_code} - {response.text}")
