import pickle
from typing import Union
from fastapi import Request
import torch
from transformers import pipeline

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "ok"}


TRANSCRIBE_PIPELINE = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-large-v3",
    torch_dtype=torch.float16,
    device="mps",
    model_kwargs={"attn_implementation": "sdpa"},
)


@app.post("/transcribe")
async def transcribe(request: Request):
    body = await request.body()
    audio_chunk = pickle.loads(body)
    outputs = TRANSCRIBE_PIPELINE.pipe(
        audio_chunk,
        chunk_length_s=30,
        batch_size=24,
        generate_kwargs={
            'task': 'transcribe',
            'language': 'english'
        },
        return_timestamps='word'
    )
    text = outputs["text"].strip()
    return {"transcribe": text}
