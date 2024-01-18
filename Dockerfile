FROM nvidia/cuda:12.3.1-devel-ubuntu20.04

RUN useradd -m -u 1000 user
USER user

RUN apt-add-repository ppa:deadsnakes/ppa \
  && apt-get update \
  && DEBIAN_FRONTEND=noninteractive \
      apt-get install --no-install-recommends --assume-yes \
        python3.11

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/code

COPY --chown=user server/pdm.lock server/pyproject.toml ./

RUN pip install pdm

RUN pdm venv create --no-symlink
RUN pdm install

COPY --from=builder --chown=user /code/.venv ./.venv

COPY --chown=user server/ ./

ENV PDM_CACHE_DIR $HOME/code/.pdm_cache/
ENV HF_HOME $HOME/code/.hf_home/

ENV DEVICE cuda:0
ENV ATTN_IMPLEMENTATION flash_attention_2

ENTRYPOINT [ "./entrypoint.sh" ]
