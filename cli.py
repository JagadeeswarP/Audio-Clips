"""
CLI Interface for US Voice Narrator Studio (Ultra-Realistic Human AI Voices)
"""

import argparse
import asyncio
import os
import sys
import io

# Force UTF-8 for console output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from voice_engine import VOICE_PRESETS, generate_speech_edge
from script_generator import SAMPLE_SCRIPTS


def main():
    parser = argparse.ArgumentParser(
        description="US Voice Narrator CLI - Ultra-Realistic Human AI Voice Generator for Shorts, Reels, Podcasts & Documentaries"
    )
    
    parser.add_argument("--text", type=str, help="Direct English text input to synthesize")
    parser.add_argument("--file", type=str, help="Path to text file containing English script")
    parser.add_argument("--sample", type=str, choices=list(SAMPLE_SCRIPTS.keys()), help="Use built-in sample script (psychology, mystery, documentary, mindset)")
    parser.add_argument("--preset", type=str, choices=list(VOICE_PRESETS.keys()), default="deep_narrator", help="Voice preset persona")
    parser.add_argument("--output", type=str, default="output_narration.mp3", help="Output MP3 filename (default: output_narration.mp3)")
    parser.add_argument("--pitch", type=str, help="Custom pitch (e.g. -4Hz, -6Hz)")
    parser.add_argument("--rate", type=str, help="Custom speaking rate (e.g. +4%, +6%)")
    parser.add_argument("--comma-pause", type=int, default=160, help="Pause duration at commas in ms")
    parser.add_argument("--period-pause", type=int, default=400, help="Pause duration at periods in ms")
    
    args = parser.parse_args()

    # Determine text content
    script_text = ""
    if args.text:
        script_text = args.text
    elif args.file:
        if not os.path.exists(args.file):
            print(f"Error: File '{args.file}' not found.", file=sys.stderr)
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            script_text = f.read()
    elif args.sample:
        script_text = SAMPLE_SCRIPTS[args.sample]["script"]
        print(f"Using sample script: {SAMPLE_SCRIPTS[args.sample]['title']}")
    else:
        # Default sample if nothing provided
        script_text = SAMPLE_SCRIPTS["psychology"]["script"]
        print("No input provided. Using default sample: Psychology Facts.")

    # Retrieve preset configuration
    preset_config = VOICE_PRESETS.get(args.preset, VOICE_PRESETS["deep_narrator"])
    
    voice = preset_config["voice"]
    pitch = args.pitch if args.pitch else preset_config["pitch"]
    rate = args.rate if args.rate else preset_config["rate"]
    volume = preset_config.get("volume", "+0%")
    comma_pause = args.comma_pause if args.comma_pause != 160 else preset_config.get("pause_comma_ms", 160)
    period_pause = args.period_pause if args.period_pause != 400 else preset_config.get("pause_period_ms", 400)

    print(f"\n--- Generating Speech ---")
    print(f"Persona Preset: {preset_config['name']}")
    print(f"Voice Engine:   {voice}")
    print(f"Pitch Adjust:   {pitch}")
    print(f"Pacing Rate:    {rate}")
    print(f"Pauses:         Commas={comma_pause}ms, Periods={period_pause}ms")
    print(f"Output File:    {args.output}")

    asyncio.run(
        generate_speech_edge(
            text=script_text,
            output_filepath=args.output,
            voice=voice,
            pitch=pitch,
            rate=rate,
            volume=volume,
            pause_comma_ms=comma_pause,
            pause_period_ms=period_pause
        )
    )

    print(f"\nSuccess! Audio saved to: {os.path.abspath(args.output)}\n")


if __name__ == "__main__":
    main()
