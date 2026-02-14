import os
import io
import soundfile as sf
import numpy as np
from typing import Optional

try:
    from kokoro_onnx import Kokoro
    KOKORO_AVAILABLE = True
except ImportError:
    KOKORO_AVAILABLE = False
    print("Warning: kokoro-onnx not installed. TTS will be disabled.")

# Singleton instance
_kokoro_instance: Optional['Kokoro'] = None

def get_kokoro():
    """Get or initialize the Kokoro singleton."""
    global _kokoro_instance
    if not KOKORO_AVAILABLE:
        return None
        
    if _kokoro_instance is None:
        # Paths to model files
        model_path = os.path.join("models", "kokoro-v1.0.onnx")
        voices_path = os.path.join("models", "voices-v1.0.bin")
        
        if os.path.exists(model_path) and os.path.exists(voices_path):
            try:
                print(f"Initializing Kokoro TTS with {model_path}...")
                _kokoro_instance = Kokoro(model_path, voices_path)
                print("Kokoro TTS initialized successfully.")
            except Exception as e:
                print(f"Error initializing Kokoro TTS: {e}")
        else:
            print(f"Warning: Kokoro model files not found at {model_path} or {voices_path}. TTS will be disabled.")
            
    return _kokoro_instance

def generate_speech(text: str, voice: str = "af_sky") -> bytes:
    """
    Generate speech from text and return WAV bytes.
    
    Args:
        text: The text to speak
        voice: The voice ID to use (default: af_sky)
        
    Returns:
        bytes: WAV audio data
    """
    kokoro = get_kokoro()
    if not kokoro:
        return b""
        
    try:
        # Generate audio samples
        # af_sarah is a good neutral professional voice
        samples, sample_rate = kokoro.create(
            text, 
            voice=voice, 
            speed=1.0, 
            lang="en-us"
        )
        
        # Convert to WAV bytes
        buffer = io.BytesIO()
        sf.write(buffer, samples, sample_rate, format='WAV')
        return buffer.getvalue()
        
    except Exception as e:
        print(f"Error generating speech: {e}")
        return b""
