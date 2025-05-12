import queue
import av
import numpy as np
import pydub
import streamlit as st
import tempfile
from streamlit_webrtc import WebRtcMode, webrtc_streamer

import httpx

from components.sidebar import make_sidebar


def transcribe(audio_segment: pydub.AudioSegment):
    with tempfile.NamedTemporaryFile(dir=".temp", suffix=".wav") as f:
        audio_segment.export(f.name, format="wav")
        with httpx.Client(timeout=None) as client:
            data = f.read()
            print(data)
            response = client.post(
                "http://localhost:8000/resources/v1/audio/text",
                content=data,
            )
            return response.json()["transcript"]


def frame_energy(frame: av.AudioFrame):
    samples = np.frombuffer(frame.to_ndarray().tobytes(), dtype=np.int16)
    return np.sqrt(np.mean(samples**2))


def add_frame_to_chunk(sound_chunk: pydub.AudioSegment, audio_frame: av.AudioFrame):
    sound = pydub.AudioSegment(
        data=audio_frame.to_ndarray().tobytes(),
        sample_width=audio_frame.format.bytes,
        frame_rate=audio_frame.sample_rate,
        channels=len(audio_frame.layout.channels),
    )
    sound_chunk += sound
    return sound_chunk


def process_audio_frame(
    audio_frames: list[av.AudioFrame],
    sound_chunk: pydub.AudioSegment,
    silence_frames: int,
    enery_threshold: int,
):
    for audio_frame in audio_frames:
        sound_chunk = add_frame_to_chunk(sound_chunk, audio_frame)

        energy = frame_energy(audio_frame)
        if energy < enery_threshold:
            silence_frames += 1
        else:
            silence_frames = 0
    return sound_chunk, silence_frames


def handle_silenece(
    sound_chunk: pydub.AudioSegment,
    silenece_frames: int,
    silence_frames_threshold: int,
    text_output,
):
    if silenece_frames >= silence_frames_threshold:
        if len(sound_chunk) > 0:
            text = transcribe(sound_chunk)
            text_output.write(text)
            sound_chunk = pydub.AudioSegment.empty()
            silenece_frames = 0

    return sound_chunk, silenece_frames


def handle_queue_empty(sound_chunk, text_output):
    if len(sound_chunk) > 0:
        text = transcribe(sound_chunk)
        text_output.write(text)
        sound_chunk = pydub.AudioSegment.empty()
    return sound_chunk


def synthesize_response(text: str):
    with httpx.Client(timeout=None) as client:
        response = client.post(
            "http://localhost:8000/resources/v1/audio/convert",
            json={"transcript": text},
        )
        uid = response.json()["uid"]
        audio_url = f"http://localhost:8000/resources/v1/audio/{uid}"
        audio_resp = client.get(audio_url)
        return audio_resp.content


def sst(
    status_indicator,
    text_output,
    timeout=3,
    energy_threshold=2000,
    silenece_frames_threshold=100,
):

    webrtc_ctx = webrtc_streamer(
        key="webrtc-app",
        mode=WebRtcMode.SENDONLY,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        audio_receiver_size=1024,
        async_processing=True,
        media_stream_constraints={"audio": True, "video": False},
    )

    sound_chunk = pydub.AudioSegment.empty()
    silence_frames = 0

    while True:
        if webrtc_ctx.audio_receiver:
            status_indicator.write("Please speak your voice")

            try:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=timeout)
            except queue.Empty:
                status_indicator.write("No frame arrived")
                sound_chunk = handle_queue_empty(sound_chunk, text_output)
                continue
            if st.session_state.muted:
                sound_chunk = handle_queue_empty(sound_chunk, text_output)
                continue
            else:
                sound_chunk, silence_frames = process_audio_frame(
                    audio_frames, sound_chunk, silence_frames, energy_threshold
                )
                sound_chunk, silence_frames = handle_silenece(
                    sound_chunk, silence_frames, silenece_frames_threshold, text_output
                )
        else:
            status_indicator.write("You are currently muted")
            if len(sound_chunk) > 0:
                text = transcribe(sound_chunk)
                text_output.write(text)
            break


def main():
    st.title("Speech to Text")
    status_indicator = st.empty()
    text_output = st.empty()

    sst(status_indicator, text_output)


main()

make_sidebar()
