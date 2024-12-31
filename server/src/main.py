import os
import pickle
from typing import Union
from fastapi import Request
import torch
from transformers import pipeline
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

from fastapi import FastAPI
from contextlib import asynccontextmanager

DEVICE = os.getenv('DEVICE', 'mps')
ATTN_IMPLEMENTATION = os.getenv('ATTN_IMPLEMENTATION', "sdpa")


@asynccontextmanager
async def lifespan(app: FastAPI):
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    # model_id = "openai/whisper-large-v3"
    model_id = "openai/whisper-large-v2"
    device = "cuda:0" if torch.cuda.is_available() else "cpu"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    app.state.transcribe_pipeline = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
    )
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
        # return_timestamps='word'
    )
    text = outputs["text"].strip()
    return {"transcribe": text, "outputs": outputs}
