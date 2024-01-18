FROM nvidia/cuda:12.3.1-devel-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y \
  && apt-get -y install software-properties-common \
  && add-apt-repository -y ppa:deadsnakes/ppa \
  && apt-get -y update \
  && apt-get install --no-install-recommends --assume-yes \
        python3.11 python3.11-distutils curl git

RUN useradd -m -u 1000 user
USER user

RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/code

COPY --chown=user server/pdm.lock server/pyproject.toml ./

RUN python3.11 -m pip install pdm

RUN pdm install

COPY --chown=user server/ ./

ENV PDM_CACHE_DIR $HOME/code/.pdm_cache/
ENV HF_HOME $HOME/code/.hf_home/

ENV DEVICE cuda:0
ENV ATTN_IMPLEMENTATION flash_attention_2

ENTRYPOINT [ "./entrypoint.sh" ]
