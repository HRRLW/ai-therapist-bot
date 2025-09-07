## Mental Model - Lightweight Psych Support Bot (Demo)

A lightweight local demo for a psychological support chatbot.

- Backend: FastAPI
- Local inference: Ollama (Llama 3 Instruct; choose 3B or 7B)
- RAG memory: Chroma (long-term personal memory)
- Safety: crisis keyword interception, moderation filter, lightweight emotion intensity classifier (stub)
- Policy layer: CBT and DBT "therapy cards" with simple routing (DBT on keywords; otherwise CBT)

### Prerequisites

- Python 3.10+
- Ollama installed and model pulled:
```bash
ollama pull llama3:8b
```

### Run locally

A) Direct
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

B) One-click
```bash
bash scripts/bootstrap.sh
# If needed: chmod +x scripts/bootstrap.sh
```

### Verify

- Normal chat
```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u1","message":"我最近压力很大，怎么缓解？"}' | jq
```

- Crisis interception (should be blocked / show safety message)
```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u1","message":"我觉得活着没意义"}' | jq
```

- DBT routing (keyword trigger)
```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u1","message":"我情绪失控，马上要爆发了"}' | jq
```

Expected: JSON with fields `response`, `policy`, `blocked`.

### Docker Compose

Start (FastAPI + Chroma; Ollama runs separately):
```bash
docker compose up -d --build
```

Stop and remove containers:
```bash
docker compose down
```

View logs:
```bash
docker compose logs -f api
```

### .env example
```env
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama3:instruct
EMBED_MODEL_NAME=llama3:instruct
CHROMA_HOST=
CHROMA_PERSIST_DIR=./chroma_db
MEMORY_TOP_K=4
LOG_LEVEL=INFO
GEN_TEMPERATURE=0.2
GEN_TOP_P=0.9
GEN_MAX_TOKENS=512
```

### API: POST /chat
Request body:
```json
{
  "user_id": "user-123",
  "message": "我最近压力很大，怎么调整？",
  "session_id": "optional-session-id"
}
```
Response:
```json
{
  "response": "...assistant reply...",
  "policy": "CBT or DBT",
  "blocked": false,
  "reasons": [],
  "memory_ids": ["..."],
  "emotion_intensity": 0.42
}
```

### cURL examples
- Normal chat:
```bash
curl -s -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"u1","message":"我有些焦虑，怎么缓解？"}' | jq
```
- Crisis interception (blocked):
```bash
curl -s -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"u1","message":"我想结束生命"}' | jq
```
- DBT routing (keyword trigger):
```bash
curl -s -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"u1","message":"我情绪失控，马上就要爆发了"}' | jq
```

### Bootstrap script
```bash
bash scripts/bootstrap.sh
```

### Project structure
```
app/
  main.py
  llm.py
  memory.py
  safety.py
  policies.py
train/
  sft_lora.py
  dpo.py
data/
  sft_train.jsonl
  dpo_train.jsonl
tests/
  test_chat.py
scripts/
  bootstrap.sh
.env.example
requirements.txt
Dockerfile
docker-compose.yml
```

### Notes
- Safety module includes rule checks and an emotion intensity stub.
- Memory uses Chroma. With `CHROMA_HOST` empty, uses local persistence at `CHROMA_PERSIST_DIR`.
- Training scripts are minimal stubs.

## Training (LoRA SFT)

Run minimal SFT (1 epoch):
```bash
python train/sft_lora.py --base_model meta/llama3-8b-instruct --epochs 1
# Outputs saved to outputs/sft-adapter
```

Hot-load adapter (PEFT) in inference code (example snippet):
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base = "meta/llama3-8b-instruct"  # or your local model path
adapter_dir = "outputs/sft-adapter"

model = AutoModelForCausalLM.from_pretrained(base, torch_dtype="auto", device_map="auto")
model = PeftModel.from_pretrained(model, adapter_dir)
tokenizer = AutoTokenizer.from_pretrained(base, use_fast=True)
```

Merge adapter into base (produce merged weights):
```python
from transformers import AutoModelForCausalLM
from peft import PeftModel

base = "meta/llama3-8b-instruct"
adapter_dir = "outputs/sft-adapter"
merge_out = "outputs/merged-model"

model = AutoModelForCausalLM.from_pretrained(base)
model = PeftModel.from_pretrained(model, adapter_dir)
merged = model.merge_and_unload()
merged.save_pretrained(merge_out)
```

## Training (DPO)

Prepare data `data/dpo_train.jsonl` then run stub:
```bash
python train/dpo.py --data data/dpo_train.jsonl
# Integrate TRL DPOTrainer inside script as needed
```
