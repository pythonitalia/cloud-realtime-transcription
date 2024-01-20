import os
import pickle
from typing import Union
from fastapi import Request
import torch
from transformers import pipeline

from fastapi import FastAPI
from contextlib import asynccontextmanager

DEVICE = os.getenv('DEVICE', 'mps')
ATTN_IMPLEMENTATION = os.getenv('ATTN_IMPLEMENTATION', "sdpa")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.transcribe_pipeline = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-large-v3",
        torch_dtype=torch.float16 if ATTN_IMPLEMENTATION == "sdpa" else torch.bfloat16,
        device=DEVICE,
        model_kwargs={"attn_implementation": ATTN_IMPLEMENTATION},
    )
    app.state.transcribe_pipeline.model.to('cuda')
    yield

app = FastAPI(lifespan=lifespan)



@app.get("/")
def read_root():
    return {"status": "ok"}



@app.post("/transcribe")
async def transcribe(request: Request):
    body = await request.body()
    audio_chunk = pickle.loads(body)
    outputs = app.state.transcribe_pipeline(
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
