FROM python:3.11

WORKDIR /code

COPY server/pdm.lock server/pyproject.toml ./

RUN pip install pdm

RUN pdm install
RUN pdm add flash_attn --no-isolation

COPY server/ ./

ENV DEVICE cuda:0
ENV ATTN_IMPLEMENTATION flash_attention_2

CMD ["./.venv/bin/uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
