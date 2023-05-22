from pytube import YouTube
import moviepy.editor as mp
import ffmpeg
import numpy as np
import openai
import json
from youtube_transcript_api import YouTubeTranscriptApi
import re

with open("tokens.json", "r") as tokens:
    TOKENS = json.load(tokens)

openai.api_key = TOKENS["openai"]

AUDIO_PATH: str = "./audio.wav"

def generate_response(url: str, question: str, timestamp: float = -1.0) -> str:
    t = transcribe_up_to_timestamp(url, timestamp)
    agent_response = call_agent(t, question, timestamp)
    return agent_response

def transcribe_up_to_timestamp(url: str, timestamp: float = -1.0, margin_seconds_after: float = 10.0) -> str:
    """
    tries to transcribe the video up to given `timestamp` + `margin_seconds_after`
    if no timestamp is specified, or if unable to get a timestamped transcript
    returns full video transcript
    """
    transcript = transcribe(url)
    if isinstance(transcript, str):
        # not annotated, return raw
        return transcript

    if timestamp < 0:
        return " ".join([sample["text"] for sample in transcript])

    result = ""
    for sample in transcript:
        if sample["start"] > timestamp + margin_seconds_after:
            break
        result += sample["text"]

    return result

def transcribe(url: str) -> str | list[dict[str, str|float]]:
    transcript = get_youtube_transcript(url)
    return transcript if transcript else whisper_transcribe(url)

def get_youtube_transcript(url: str) -> list[dict[str, str|float]] | None:
    """
    returns a list of json objects for each
    of the caption instances.
    This does not necessarily corresponds to the actual video transcript,
    but is always a good additional signal, and possibly a shortcut around 
    speech-to-txt such as whisper

    For example:
    [{"text": "Vsauce! Kevin here -- and happiness is depressing. There is no more seminal",
      "start": 0.0,
      "end": 6.06
    },{"text": "human concept than the pursuit of happiness -- a nation was built around the right to do",
       "start": 6.06,
       "end": 11.52}]
    """

    # look for everything from `?v=` or `&v=` up to `&` or the end of the string
    pattern = re.compile(r"[\?|\&]v=([^\&]*)")
    video_id = pattern.search(url).group(1)
    if not video_id:
        return None
    english_locales = ["en", "en-US", "en-GB", "en-AU", "en-IN",
                   "en-CA", "en-NZ", "en-IE", "en-PH", "en-BZ", "en-CB",
                   "en-JM", "en-ZA", "en-TT"]
    transcripts = YouTubeTranscriptApi.list_transcripts("9nVL9nSix1A")
    try:
        transcript_obj = transcripts.find_manually_created_transcript(english_locales)
    except:
        return None
    transcript = transcript_obj.fetch()
    return [{
        "text": caption.get("text", "").strip().replace('\xa0', '').replace('\n', ' '),
        "start": caption.get("start", 0.0),
        "end": caption.get("start", 0.0) + caption.get("duration", 0.0)
    } for caption in transcript]

def whisper_transcribe(url) -> str:
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

    return w.transcribe(arr)

def call_agent(transcript: str, question: str, timestamp: float = 0.0) -> str:
    system_msg = f"""
Pretend you are the youtuber. You made a youtube video. Here is the transcript of that video:

<transcript>
{transcript}
</transcript>

Now your sole goal is to answer user"s questions about that video.
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": question},
            ]
    )

    result = ""
    for choice in response.choices:
        result += choice.message.content

    return result