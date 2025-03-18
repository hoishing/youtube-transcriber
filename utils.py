from groq import Groq
from pytubefix import Buffer, YouTube


def transcribe(api_key: str, url: str, lang: str = None) -> str:
    """
    Transcribe a YouTube video using Groq's audio transcription API.

    Args:
        api_key: Groq API key for authentication
        url: URL of the YouTube video to transcribe
        lang: Optional language code for the transcription (default: None, auto-detect)
            possible values such as "en", "zh", "yue" ... etc.
            see Groq API `client.audio.transcriptions.create` for more details.

    Returns:
        Transcribed text from the video's audio
    """
    yt = YouTube(url)
    audio_stream = yt.streams.get_audio_only()

    buffer = Buffer()
    buffer.download_in_buffer(audio_stream)

    client = Groq(api_key=api_key)
    params = dict(
        file=(f"{yt.video_id}.mp4", buffer.read()),
        model="whisper-large-v3",
        response_format="text",
        temperature=0.0,
    )

    if lang is not None:
        params["language"] = lang

    return client.audio.transcriptions.create(**params)


def add_punctuation(api_key: str, transcript: str) -> str:
    """
    Add punctuation to a transcript using Groq's LLM.

    Args:
        api_key: Groq API key for authentication
        transcript: Transcribed text from the video's audio

    Returns:
        Transcript with punctuation added
    """
    client = Groq(api_key=api_key)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "add punctuation to the following text, just output the text with punctuation, no other text",
            },
            {
                "role": "user",
                "content": transcript,
            },
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content
