#!/bin/bash

./.venv/bin/ninja --version
echo $?

cd $HOME/code
ls -al
ls .venv/ -al
ls .venv/bin/ -al
ls .venv/lib/python3.11/site-packages/ -al

curl -sS https://bootstrap.pypa.io/get-pip.py | ./.venv/bin/python
./.venv/bin/python -m pip install flash_attn==1.0.9 --no-build-isolation

echo "Installation done"

./.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 7860
