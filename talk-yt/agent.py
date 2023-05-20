from pytube import YouTube
import moviepy.editor as mp
import ffmpeg
import numpy as np
import openai
import json

TOKENS = json.load("tokens.json")

openai.api_key = TOKENS["openai"]

AUDIO_PATH: str = "./audio.wav"

def generate_response(url: str, question: str, timestamp: float = 0.0) -> str:
    youtube = YouTube(url)
    video = youtube.streams.get_audio_only()
    video.download(output_path="./", filename="audio.mp4")

    # Convert the downloaded video to WAV format using moviepy
    clip = mp.AudioFileClip("audio.mp4")
    clip.write_audiofile("audio.wav")

    # Clean up the temporary video file
    clip.close()

    try:
        y, _ = (
            ffmpeg.input(AUDIO_PATH, threads=0)
            .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=16000)
            .run(
                cmd=["ffmpeg", "-nostdin"], capture_stdout=True, capture_stderr=True
            )
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

    arr = np.frombuffer(y, np.int16).flatten().astype(np.float32) / 32768.0

    from whispercpp import Whisper

    w = Whisper.from_pretrained("base.en")

    t = w.transcribe(arr)
    agent_response = call_agent(t, question, timestamp)
    return agent_response

def call_agent(transcript: str, question: str, timestamp: float = 0.0) -> str:
    system_msg = f"""
Pretend you are the youtuber. You made a youtube video. Here is the transcript of that video:

<transcript>
{transcript}
</transcript>

Now your sole goal is to answer user's questions about that video.
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": question},
            ]
    )

    result = ''
    for choice in response.choices:
        result += choice.message.content

    return result