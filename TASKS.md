# VIS Build Tasks — 3-Agent System

Legend: [ ] = pending · [x] = done · [~] = in progress

---

## Phase 1 — Foundation
- [x] Task 01: `requirements.txt` + `.env.example`
- [x] Task 02: `data/models.py` — all Pydantic v2 models
- [x] Task 03: `config/settings.py` + `venue_layout.json` + `thresholds.yaml`
- [x] Task 04: `core/state_store.py` — in-memory venue state
- [x] Task 05: `core/event_bus.py` — asyncio pub/sub
- [x] Task 06: `core/ingestion.py` — normalize + threshold gate + publish

## Phase 2 — Real-Time Data
- [x] Task 07: `scripts/simulate_realtime.py` — live sensor events every 2s

## Phase 3 — Rule Engine
- [x] Task 08: `rules/engine.py` — crowd routing, queue, parking, staff dispatch rules

## Phase 4 — AI Agents
- [x] Task 09: `core/client.py` — Anthropic client + prompt caching
- [x] Task 10: `agents/base_agent.py` — shared Claude agentic loop
- [x] Task 11: `agents/attendee/` — chat agent (seat, food, accessibility)
- [x] Task 12: `agents/emergency/` — emergency agent (PA, evacuation, EMS)
- [x] Task 13: `agents/vision_anomaly/` — Claude Vision anomaly interpretation

## Phase 5 — API
- [x] Task 14: `api/main.py` — FastAPI app + lifespan
- [x] Task 15: `api/routes/events.py` — POST /events/sensor
- [x] Task 16: `api/routes/attendee.py` — WebSocket /ws/attendee/{id}
- [x] Task 17: `api/routes/ops.py` — GET /ops/status
- [x] Task 18: `main.py` — entry point, wire everything

## Phase 6 — Tests
- [ ] Task 19: `tests/test_rules.py`
- [ ] Task 20: `tests/test_agents.py`
- [ ] Task 21: `tests/test_api.py`
