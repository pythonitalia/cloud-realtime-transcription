FROM python:3.11

RUN useradd -m -u 1000 user
USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/code

ENV PDM_CACHE_DIR $HOME/code/.pdm_cache/
ENV HF_HOME $HOME/code/.hf_home/

COPY --chown=user server/pdm.lock server/pyproject.toml ./

RUN pip install pdm

RUN pdm install

COPY --chown=user server/ ./

ENV DEVICE cuda:0
ENV ATTN_IMPLEMENTATION flash_attention_2

ENTRYPOINT [ "./entrypoint.sh" ]
