import sounddevice
from starlette.responses import PlainTextResponse

import threading
from starlette.applications import Starlette
from starlette.routing import Route
from sse_starlette.sse import EventSourceResponse
import uvicorn
import asyncio
import numpy as np
import time
import os
import httpx
from queue import Queue
import logging
from datetime import UTC, datetime, timedelta
from time import sleep
import pickle

import speech_recognition as sr
from starlette.middleware import Middleware
from audio_utils import get_microphone, get_speech_recognizer, get_all_audio_queue, to_audio_array, AudioChunk
from starlette.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

TRANSCRIBING_SERVER = os.getenv('TRANSCRIBING_SERVER', "http://localhost:3535/transcribe")


def main(transcriptions_queue):
    recording_duration = 1
    sample_rate = 16000
    energy_threshold = 300

    data_queue = Queue()
    microphone = get_microphone(sample_rate=sample_rate)
    print('microphone is:', microphone)

    with microphone:
        speech_recognizer = get_speech_recognizer(energy_threshold=energy_threshold)
        speech_recognizer.adjust_for_ambient_noise(source=microphone)

    def record_callback(_, audio: sr.AudioData) -> None:
        data = audio.get_raw_data()
        data_queue.put(data)

    speech_recognizer.listen_in_background(source=microphone, callback=record_callback, phrase_time_limit=recording_duration)

    print("\n🎤 Microphone is now listening...\n")

    prev_audio_array = None
    current_audio_chunk = AudioChunk(start_time=datetime.now(tz=UTC))

    while True:
        try:
            now = datetime.now(tz=UTC)
            # Pull raw recorded audio from the queue.
            if not data_queue.empty():
                # Store end time if we're over the recording time limit.
                if now - current_audio_chunk.start_time > timedelta(seconds=recording_duration):
                    current_audio_chunk.end_time = now

                # Get audio data from queue
                audio_data = get_all_audio_queue(data_queue)
                audio_np_array = to_audio_array(audio_data)

                if current_audio_chunk.is_complete:
                    print('start serialize')
                    if prev_audio_array is not None:
                        serialized = pickle.dumps(
                            np.concatenate((
                                prev_audio_array,
                                current_audio_chunk.audio_array
                            ))
                        )
                    else:
                        serialized = pickle.dumps(current_audio_chunk.audio_array)
                    prev_audio_array = current_audio_chunk.audio_array
                    print('end serialize')

                    start = time.time()
                    print('start req')
                    response = httpx.post(TRANSCRIBING_SERVER, data=serialized)
                    print('req status', response.status_code)
                    full_json = response.json()
                    transcription = full_json['transcribe']
                    print('req done -> full json', full_json, 'status code', response.status_code, 'time', time.time() - start)
                    transcriptions_queue.put(transcription)

                    # text = transcribe_model.transcribe(current_audio_chunk.audio_array)
                    # sentence = Sentence(
                    #     start_time=current_audio_chunk.start_time, end_time=current_audio_chunk.end_time, text=text
                    # )
                    current_audio_chunk = AudioChunk(
                        audio_array=audio_np_array, start_time=datetime.now(tz=UTC)
                    )
                    # print(sentence.text)  # noqa: T201
                else:
                    current_audio_chunk.update_array(audio_np_array)

                # Flush stdout
                print("", end="", flush=True)  # noqa: T201

                # Infinite loops are bad for processors, must sleep.
                sleep(0.25)
        except KeyboardInterrupt:
            current_audio_chunk.end_time = datetime.now(tz=UTC)
            if current_audio_chunk.is_complete:
                logger.warning("⚠️ Transcribing last chunk...")
                # text = transcribe_model.transcribe(current_audio_chunk.audio_array)
                # sentence = Sentence(
                #     start_time=current_audio_chunk.start_time, end_time=current_audio_chunk.end_time, text=text
                # )
                # print(sentence.text)  # noqa: T201
            break


    # for i in range(minimum, maximum + 1):
    #     await asyncio.sleep(0.9)
    #     yield dict(data=i)

async def sse(request):
    async def event_publisher():
        try:
            while True:
                text = transcriptions_queue.get()
                yield dict(data=text)
                await asyncio.sleep(0.2)
        except asyncio.CancelledError as e:
            print(f"Disconnected from client (via refresh/close) {request.client}")

    return EventSourceResponse(event_publisher())


def test(request):
    return PlainTextResponse("test")

routes = [
    Route('/', endpoint=test),
    Route("/test", endpoint=sse)
]

app = Starlette(
    debug=True,
    routes=routes,
    middleware=[
        Middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])
    ],
)


def server(transcriptions_queue):
    app.state.transcriptions_queue = transcriptions_queue
    uvicorn.run(app, host="0.0.0.0", port=8343, log_level='info')


if __name__ == '__main__':
    transcriptions_queue = Queue()

    main_thread = threading.Thread(target=main, args=(transcriptions_queue,))
    main_thread.start()

    server_thread = threading.Thread(target=server, args=(transcriptions_queue,))
    server_thread.start()

    main_thread.join()
    server_thread.join()
