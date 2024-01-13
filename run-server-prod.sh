cd server

DEVICE=cuda:0 ATTN_IMPLEMENTATION=flash_attention_2 ./.venv/bin/uvicorn src.main:app --host 0.0.0.0 --reload --port 3535
cd -
