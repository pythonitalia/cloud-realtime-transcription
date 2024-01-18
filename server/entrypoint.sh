#!/bin/bash

cd $HOME/code
ls -al

./.venv/bin/pip install flash_attn --no-build-isolation

echo "Installation done"

./.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 7860
