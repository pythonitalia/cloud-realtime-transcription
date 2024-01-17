FROM python:3.11

WORKDIR /code

COPY server/pdm.lock server/pyproject.toml ./

RUN pip install pdm

RUN pdm install

COPY server/ ./

ENV DEVICE cuda:0
ENV ATTN_IMPLEMENTATION flash_attention_2

ENTRYPOINT [ "./entrypoint.sh" ]
