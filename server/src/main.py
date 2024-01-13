from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "ok"}


@app.post("/transcribe")
def transcribe(audio: bytes):
    return {"transcribe": "hello"}
