import httpx
from queue import Queue
import logging
from datetime import UTC, datetime, timedelta
from time import sleep
import pickle

import speech_recognition as sr

from audio_utils import get_microphone, get_speech_recognizer, get_all_audio_queue, to_audio_array, AudioChunk

logger = logging.getLogger(__name__)

TRANSCRIBING_SERVER = "http://localhost:3535/transcribe"


def main():
    recording_duration = 2
    sample_rate = 16000
    energy_threshold = 300

    data_queue = Queue()

    microphone = get_microphone(sample_rate=sample_rate)
    speech_recognizer = get_speech_recognizer(energy_threshold=energy_threshold)

    with microphone:
        speech_recognizer.adjust_for_ambient_noise(source=microphone)

    def record_callback(_, audio: sr.AudioData) -> None:
        data = audio.get_raw_data()
        data_queue.put(data)

    speech_recognizer.listen_in_background(source=microphone, callback=record_callback)

    print("\n🎤 Microphone is now listening...\n")

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
                    serialized = pickle.dumps(current_audio_chunk.audio_array)

                    response = httpx.post(TRANSCRIBING_SERVER, data=serialized)
                    print('chunk done', response.text, response.status_code)

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


if __name__ == '__main__':
    main()