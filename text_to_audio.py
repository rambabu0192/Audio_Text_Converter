from gtts import gTTS
from deep_translator import GoogleTranslator
import os
from datetime import datetime


def translate_text(text, target_language):

    translated_text = GoogleTranslator(
        source="auto",
        target=target_language
    ).translate(text)

    return translated_text


def convert_text_to_audio(text, language="en"):

    # Create outputs folder
    os.makedirs("outputs", exist_ok=True)

    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_path = f"outputs/audio_{timestamp}.mp3"

    # Generate audio
    audio = gTTS(
        text=text,
        lang=language
    )

    audio.save(output_path)

    return output_path