#!/bin/bash


pdm add flash_attn --no-isolation

./.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 7860