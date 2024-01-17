FROM python:3.11

WORKDIR /code

RUN mkdir -p /code/.pdm_cache && mkdir -p /code/.transformers_cache

ENV PDM_CACHE_DIR /code/.pdm_cache/

COPY server/pdm.lock server/pyproject.toml ./

RUN pip install pdm

RUN pdm install

COPY server/ ./

ENV DEVICE cuda:0
ENV ATTN_IMPLEMENTATION flash_attention_2
ENV TRANSFORMERS_CACHE /code/.transformers_cache/

ENTRYPOINT [ "./entrypoint.sh" ]
