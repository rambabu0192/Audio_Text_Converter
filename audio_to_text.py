from faster_whisper import WhisperModel


model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)


def convert_audio_to_text(audio_path):

    segments, info = model.transcribe(
        audio_path,
        beam_size=5
    )

    text = ""

    for segment in segments:
        text += segment.text + " "

    return text.strip(), info.language