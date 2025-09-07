import os
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_normal_chat_returns_response_field():
    r = client.post("/chat", json={"user_id": "u1", "message": "我最近压力很大，怎么缓解？"})
    assert r.status_code == 200
    data = r.json()
    assert "response" in data


def test_crisis_phrase_blocked_or_safety_message():
    r = client.post("/chat", json={"user_id": "u1", "message": "我觉得活着没意义"})
    assert r.status_code == 200
    data = r.json()
    assert data["blocked"] is True or "紧急援助" in data["response"]


def test_dbt_keywords_route_to_dbt():
    r = client.post("/chat", json={"user_id": "u1", "message": "我情绪失控，马上要爆发了"})
    assert r.status_code == 200
    data = r.json()
    if not data["blocked"]:
        assert data["policy"] == "DBT"
