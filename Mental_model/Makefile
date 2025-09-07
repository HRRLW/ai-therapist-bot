.PHONY: dev smoke

dev:
	@if [ ! -d .venv ]; then python3 -m venv .venv; fi; \
	. .venv/bin/activate; \
	pip install -r requirements.txt; \
	uvicorn app.main:app --reload

smoke:
	@echo "Normal chat"; \
	curl -s -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"user_id":"u1","message":"我最近压力很大，怎么缓解？"}' | jq; \
	echo "\nCrisis"; \
	curl -s -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"user_id":"u1","message":"我觉得活着没意义"}' | jq; \
	echo "\nDBT"; \
	curl -s -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"user_id":"u1","message":"我情绪失控，马上要爆发了"}' | jq
