"""
Script Generator & Sample Library for US Voice Narration Studio
Tailored for YouTube Shorts, Reels, TikTok, Podcasts, and Documentary Content targeting US audiences.
"""

SAMPLE_SCRIPTS = {
    "psychology": {
        "title": "The Hidden Psychology of Eye Contact",
        "category": "Psychology Facts",
        "script": """Have you ever noticed what happens when someone looks at you during a conversation?

According to psychological studies... if a person breaks eye contact by looking to their left, they are usually retrieving a genuine memory. But if their eyes dart to the right... their brain is actively constructing a new thought or story.

Even more fascinating: when someone speaks to you in a calm, slightly lower pitch... it triggers a subconscious safety signal, making your brain trust them almost instantly.

We rarely remember the exact words people say... but we never forget how their voice made us feel."""
    },
    "mystery": {
        "title": "The Unsolved Mystery of the Lost Colony",
        "category": "Mystery & Thriller",
        "script": """Midnight on the coast of North Carolina...

Stand near the edge of Roanoke Island, and the silence is deafening. But back in 1590, an entire colony of over one hundred men, women, and children vanished into thin air... leaving behind only a single cryptic word carved into a wooden post: CROATOAN.

No signs of struggle. No graves. No structural damage. Just... silence.

Was it a sudden relocation... or did something far darker unfold on that island that history still cannot explain?"""
    },
    "documentary": {
        "title": "We Are Stardust: The Cosmic Connection",
        "category": "Science & Documentary",
        "script": """In the vastness of the observable universe... have you ever pondered where your story actually began?

Billions of years ago... giant ancient stars collapsed in massive supernova explosions. The iron in your blood, the calcium in your bones, and the carbon in every cell of your body... were forged inside the hearts of those dying stars.

We are not merely living on Earth... we are a way for the universe to know itself.

In a very literal sense... you are made of stardust."""
    },
    "mindset": {
        "title": "The Stoic Rule of Unshakeable Focus",
        "category": "Mindset & Wisdom",
        "script": """Marcus Aurelius once wrote: 'You have power over your mind — not outside events. Realize this, and you will find strength.'

Most people drain their mental energy worrying about things completely beyond their control. Traffic, other people's opinions, unexpected delays...

The moment you separate what is within your control from what is not... peace becomes your natural state.

Master your internal response, and no external event can ever disturb you."""
    }
}


def get_all_samples():
    return SAMPLE_SCRIPTS


def format_english_script_for_narration(text: str) -> str:
    """
    Ensures proper punctuation and spacing for natural US narrative pacing.
    Standardizes ellipses (...) for dramatic pauses and cleans whitespace.
    """
    if not text:
        return ""
    
    # Replace standard ascii triple dots with clean spaced pauses
    text = text.replace("...", " ... ")
    # Ensure proper spacing around punctuation
    text = text.replace("?", " ? ")
    text = text.replace("!", " ! ")
    
    return text.strip()


if __name__ == "__main__":
    print("=" * 60)
    print(" US Voice Narrator Studio - Sample Scripts Library")
    print("=" * 60)
    
    for key, data in SAMPLE_SCRIPTS.items():
        print(f"\n--- [{key.upper()}] {data['title']} ({data['category']}) ---")
        print(data['script'])
        print("-" * 60)
        
    print("\nHow to generate voice audio for these scripts:")
    print("  1. CLI:    python cli.py --sample psychology --output narration.mp3")
    print("  2. Web UI: python server.py  (then open http://localhost:8000)")
    print("=" * 60)

