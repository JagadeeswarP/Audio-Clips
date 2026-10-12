import os
import uuid
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from voice_engine import (
    VOICE_PRESETS,
    VOICE_OPTIONS,
    generate_speech_edge,
    generate_speech_elevenlabs,
    preprocess_english_text,
    text_to_ssml
)
from script_generator import get_all_samples

app = FastAPI(
    title="US Voice Narrator Studio",
    description="Ultra-Realistic Human AI Voice Studio for US Content Creators",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create output directory for generated audio files
AUDIO_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generated_audio")
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

# Edge TTS is convenient for local use but Microsoft's public endpoint can deny
# requests from cloud-hosting IP ranges. Set TTS_PROVIDER=elevenlabs and provide
# ELEVENLABS_API_KEY on a hosted deployment for a supported production path.
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "edge").lower()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")


class SpeechRequest(BaseModel):
    text: str = Field(..., description="Script text to synthesize")
    preset: str = Field(default="deep_narrator", description="Voice preset name")
    voice: str = Field(default="en-US-GuyNeural", description="Edge TTS US voice name")
    pitch: str = Field(default="-4Hz", description="Pitch adjustment e.g. -4Hz for deep baritone")
    rate: str = Field(default="+4%", description="Pacing rate e.g. +4% for natural narration")
    volume: str = Field(default="+0%", description="Volume shift e.g. +0%")
    comma_pause: int = Field(default=160, description="Pause duration at commas in milliseconds")
    period_pause: int = Field(default=400, description="Pause duration at periods in milliseconds")


@app.get("/api/presets")
def get_presets():
    """Returns available voice presets."""
    return JSONResponse(content={"presets": VOICE_PRESETS})


@app.get("/api/voices")
def get_voices():
    """Returns supported US English neural voices."""
    return JSONResponse(content={"voices": VOICE_OPTIONS})


@app.get("/api/samples")
def get_samples():
    """Returns sample English scripts."""
    return JSONResponse(content={"samples": get_all_samples()})


@app.post("/api/ssml-preview")
def preview_ssml(request: SpeechRequest):
    """Generates SSML preview string with human pause markers."""
    ssml = text_to_ssml(
        text=request.text,
        voice=request.voice,
        pitch=request.pitch,
        rate=request.rate,
        volume=request.volume,
        pause_comma_ms=request.comma_pause,
        pause_period_ms=request.period_pause
    )
    return JSONResponse(content={"ssml": ssml})


@app.post("/api/generate")
async def generate_speech(request: SpeechRequest):
    """Synthesizes speech and returns file metadata and stream link."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text script cannot be empty.")

    filename = f"narration_{uuid.uuid4().hex[:8]}.mp3"
    filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)

    try:
        if TTS_PROVIDER == "elevenlabs":
            if not ELEVENLABS_API_KEY:
                raise HTTPException(
                    status_code=503,
                    detail="ElevenLabs is selected but ELEVENLABS_API_KEY is not configured."
                )
            await asyncio.to_thread(
                generate_speech_elevenlabs,
                request.text,
                filepath,
                ELEVENLABS_API_KEY,
                ELEVENLABS_VOICE_ID,
            )
        else:
            await generate_speech_edge(
                text=request.text,
                output_filepath=filepath,
                voice=request.voice,
                pitch=request.pitch,
                rate=request.rate,
                volume=request.volume,
                pause_comma_ms=request.comma_pause,
                pause_period_ms=request.period_pause
            )

        return JSONResponse(content={
            "success": True,
            "filename": filename,
            "audio_url": f"/audio/{filename}",
            "voice": request.voice,
            "file_size": os.path.getsize(filepath)
        })
    except HTTPException:
        raise
    except Exception as e:
        if TTS_PROVIDER == "edge" and "403" in str(e):
            raise HTTPException(
                status_code=503,
                detail=(
                    "Microsoft Edge TTS denied this cloud-hosted request. "
                    "Configure a supported provider by setting TTS_PROVIDER=elevenlabs "
                    "and ELEVENLABS_API_KEY in Render."
                )
            )
        raise HTTPException(status_code=500, detail=f"Speech synthesis error: {str(e)}")


@app.get("/audio/{filename}")
def download_audio(filename: str):
    """Serves synthesized audio MP3 files."""
    filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Audio file not found.")
    return FileResponse(filepath, media_type="audio/mpeg", filename=filename)


# Mount public directory for Web UI static files
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "public")
os.makedirs(PUBLIC_DIR, exist_ok=True)
app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    print("Starting US Voice Studio Server on http://localhost:8000 ...")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
