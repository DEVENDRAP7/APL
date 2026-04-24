# Venue Intelligence System (VIS)
### AI-Powered Multi-Agent Ecosystem for Large-Scale Sporting Venues

---

## Execution Model: Sequential vs Parallel

| Stage | Pattern | File |
|---|---|---|
| Event arrives → Orchestrator classifies | **Sequential** | `api/routes/events.py` |
| Orchestrator → multiple sub-agents | **Parallel** (`asyncio.gather`) | `agents/orchestrator/agent.py` |
| Within one agent's LLM agentic loop | **Sequential** | `agents/base_agent.py` |
| Multiple tool calls in one LLM response | **Parallel** (`asyncio.gather`) | `tools/registry.py` |
| Emergency: route check → evacuation trigger | **Sequential** (enforced) | `agents/emergency_response/agent.py` |
| High-priority broadcast to all agents | **Parallel** | `core/event_bus.py` |
| Attendee stream + Orchestrator metadata | **Parallel** (two async tasks) | `api/routes/attendee.py` |
| State write → next Orchestrator read | **Sequential** | `core/state_store.py` |

**Rule of thumb:** Fan-out (one event → many agents) is always parallel. Fan-in (many results → one decision) and LLM loops are always sequential.

---

## Problem Statement

Large sporting venues (50,000–100,000+ attendees) face systemic challenges that degrade the attendee experience and strain operational staff:

- **Crowd bottlenecks** at entry gates, concourses, and post-event exits
- **Long wait times** at concessions, restrooms, and merchandise stands
- **Poor real-time coordination** between security, medics, ushers, and logistics staff
- **Slow emergency response** due to siloed communication systems
- **No personalized attendee guidance** for seat finding, accessibility, or food ordering
- **Reactive (not predictive)** parking and transport management

**Solution:** A multi-agent AI system powered by the Anthropic Claude API that coordinates nine specialized agents in real time — each owning a domain, all orchestrated by a central intelligence layer.

---

## System Architecture

```
                        ┌────────────────────────────────────┐
                        │         VenueOrchestrator          │
    External Events ───►│   claude-opus-4-7 (adaptive)       │◄── Admin Controls
    Sensor Feeds        │   Event routing · State management  │    WebSocket Clients
                        └──────────────┬─────────────────────┘
                                       │ delegates via tool calls
           ┌───────────────────────────┼───────────────────────────┐
           │               │           │           │               │
    ┌──────▼──────┐  ┌─────▼─────┐  ┌─▼─────────┐ │  ┌──────────▼──┐
    │  CrowdFlow  │  │ WaitTime  │  │   Staff   │ │  │  Emergency  │
    │    Agent    │  │   Agent   │  │   Coord.  │ │  │  Response   │
    │ sonnet-4-6  │  │ sonnet-4-6│  │ sonnet-4-6│ │  │  opus-4-7   │
    └─────────────┘  └───────────┘  └───────────┘ │  └─────────────┘
           │               │                       │
    ┌──────▼──────┐  ┌─────▼─────┐  ┌─────────────▼──┐  ┌──────────┐
    │  Attendee   │  │  Parking  │  │ Infrastructure  │  │Analytics │
    │ Experience  │  │ Transport │  │    Monitor      │  │ Insight  │
    │ sonnet-4-6  │  │ sonnet-4-6│  │   sonnet-4-6    │  │sonnet-4-6│
    └─────────────┘  └───────────┘  └─────────────────┘  └──────────┘
```

**Three coordination patterns:**
1. **Orchestrator-Subagent** — All cross-domain decisions flow through the Orchestrator
2. **Event-Driven Broadcast** — Critical sensor thresholds activate agents in parallel
3. **Streaming Handoff** — AttendeeExperienceAgent streams to mobile WebSocket while returning structured metadata to Orchestrator

---

## Agent Roster

| # | Agent | Model | Domain | Streaming |
|---|---|---|---|---|
| 0 | **VenueOrchestrator** | `claude-opus-4-7` | Central routing, state, mode management | No |
| 1 | **CrowdFlowAgent** | `claude-sonnet-4-6` | Density monitoring, bottleneck detection, gate control | Yes (alerts) |
| 2 | **WaitTimeAgent** | `claude-sonnet-4-6` | Queue management, concessions, staff redeployment | No |
| 3 | **StaffCoordinationAgent** | `claude-sonnet-4-6` | Dispatch, radio comms, incident logging | No |
| 4 | **EmergencyResponseAgent** | `claude-opus-4-7` | Medical, security, fire, evacuation | Yes (PA generation) |
| 5 | **AttendeeExperienceAgent** | `claude-sonnet-4-6` | Chat, seat finding, food orders, accessibility | Yes (chat) |
| 6 | **ParkingTransportAgent** | `claude-sonnet-4-6` | Parking, shuttles, rideshare, transit feeds | No |
| 7 | **InfrastructureMonitorAgent** | `claude-sonnet-4-6` | Power, HVAC, AV, network, structural sensors | No |
| 8 | **AnalyticsInsightAgent** | `claude-sonnet-4-6` | KPIs, dashboards, historical comparison, forecasting | No |

---

## Tool Inventory

### VenueOrchestrator
| Tool | Purpose |
|---|---|
| `query_venue_state` | Read holistic venue snapshot from Redis |
| `delegate_to_agent` | Programmatic sub-agent invocation with typed payload |
| `broadcast_alert` | Push alert to all notification channels simultaneously |
| `escalate_emergency` | Switch EmergencyAgent to Opus reasoning, take direct command |
| `fetch_historical_pattern` | Retrieve crowd/incident patterns for current event type |
| `set_venue_mode` | Transition: `pre_event → gates_open → in_event → post_event → emergency → evacuation` |

### CrowdFlowAgent
| Tool | Purpose |
|---|---|
| `get_sensor_grid` | IoT crowd density readings per zone |
| `get_camera_analytics` | CV-processed headcount + movement vectors |
| `predict_congestion` | ML time-series forecast (5–60 min horizon) |
| `redirect_signage` | Update digital signs with directional messages |
| `open_auxiliary_gate` | Open extra gates when density > 70% |
| `notify_usher_team` | Radio + app instruction to zone ushers |

### WaitTimeAgent
| Tool | Purpose |
|---|---|
| `get_queue_depth` | Queue sensor / camera data per location |
| `get_pos_throughput` | POS transaction rate (items/min per station) |
| `adjust_staff_allocation` | Redeploy staff count at a location |
| `push_attendee_notification` | Mobile push to individual attendee |
| `update_wait_display` | Update public wait time display boards |
| `get_menu_availability` | Inventory levels per concession stand |

### StaffCoordinationAgent
| Tool | Purpose |
|---|---|
| `get_staff_roster` | Active staff list with GPS locations |
| `dispatch_staff` | Assign staff to location + task |
| `send_radio_message` | Push to radio channel |
| `get_staff_location` | Real-time GPS tracker |
| `request_mutual_aid` | Request external agency resources |
| `log_incident` | Structured incident record |
| `update_staff_status` | Update staff availability status |

### EmergencyResponseAgent
| Tool | Purpose |
|---|---|
| `trigger_evacuation` | Activates PA + signage + staff + external services simultaneously |
| `contact_external_service` | EMS, police, fire — `immediate` priority triggers 911 relay |
| `activate_pa_system` | PA broadcast with tone: `informational / urgent / emergency` |
| `get_evacuation_route_status` | Real-time exit capacity + obstruction check |
| `lock_zone` | One-way gate lock (exit allowed, entry blocked) |
| `deploy_aed` | Dispatch AED unit to location |
| `create_incident_report` | Structured incident record for authorities |

### AttendeeExperienceAgent
| Tool | Purpose |
|---|---|
| `lookup_seat` | Seat location + walking directions from attendee's current zone |
| `find_nearest_accessible_route` | Wheelchair/mobility-accessible path |
| `place_food_order` | Order to concession with delivery to seat |
| `get_menu` | Current menu + availability per stand |
| `locate_amenity` | Find nearest restroom, first aid, ATM, etc. |
| `report_lost_item` | Log lost & found report |
| `get_schedule_update` | Live event timeline (delays, halftime, etc.) |
| `request_wheelchair_assistance` | Dispatch mobility assistance staff |

### ParkingTransportAgent
| Tool | Purpose |
|---|---|
| `get_parking_availability` | Real-time lot occupancy |
| `open_parking_zone` | Activate overflow lot |
| `update_dynamic_signage` | Parking directional sign update |
| `coordinate_rideshare_zone` | Manage Uber/Lyft staging capacity |
| `dispatch_shuttle` | Add extra buses to a route |
| `get_transit_status` | Public transit real-time feeds |
| `predict_exit_surge` | Forecast vehicle volume at N minutes |
| `notify_parking_attendants` | Instructions to lot staff |

### InfrastructureMonitorAgent
| Tool | Purpose |
|---|---|
| `get_sensor_reading` | BMS/IoT sensor reading (power, temp, structural) |
| `get_system_status` | HVAC, power, AV, network status |
| `alert_facilities` | Notify facilities team with severity |
| `dispatch_maintenance` | Send maintenance crew to location |
| `toggle_system` | Control HVAC zones, lighting, etc. |
| `get_power_consumption` | Live power draw per zone |
| `check_network_health` | Network latency + packet loss metrics |

### AnalyticsInsightAgent
| Tool | Purpose |
|---|---|
| `aggregate_metrics` | Roll up KPIs across a time window |
| `generate_report` | Produce formatted report (pre/in/post event) |
| `get_revenue_snapshot` | Live revenue across all concession points |
| `compare_to_historical` | Benchmark current metrics vs. past events |
| `export_dashboard_data` | Export data for operations dashboard |
| `query_event_log` | Filtered search of all system events |
| `predict_revenue` | Scenario-based revenue forecast |

---

## Key Data Models

All models in `data/models.py` using **Pydantic v2**.

```python
# Live venue state (Redis-backed, <1s TTL)
class ZoneState(BaseModel):
    zone_id: str
    current_occupancy: int
    occupancy_pct: float
    flow_rate: float                    # people/minute
    flow_direction: str                 # inbound | outbound | mixed
    queue_depth: int
    wait_time_minutes: float
    alert_level: Literal["normal", "elevated", "critical", "emergency"]
    timestamp: datetime

class VenueState(BaseModel):
    venue_id: str
    operational_mode: Literal["pre_event", "gates_open", "in_event",
                               "post_event", "emergency", "evacuation"]
    overall_alert_level: Literal["normal", "elevated", "critical", "emergency"]
    zones: dict[str, ZoneState]
    active_incidents: list[Incident]
    staff_deployments: dict[str, StaffDeployment]
    timestamp: datetime

# Event flowing into the system from sensors
class SensorEvent(BaseModel):
    event_id: str
    sensor_id: str
    zone_id: str
    sensor_type: Literal["crowd_density", "queue_depth", "temperature",
                          "power", "network", "access_control"]
    value: float
    severity: Literal["info", "warning", "critical"]
    threshold_breached: bool
    timestamp: datetime

# Inter-agent communication
class AgentEvent(BaseModel):
    event_id: str
    source_agent: str
    target_agent: str               # "orchestrator" | agent_name | "broadcast"
    event_type: str
    priority: Literal["low", "medium", "high", "emergency"]
    payload: dict
    requires_acknowledgment: bool
    timestamp: datetime

# Incident record
class Incident(BaseModel):
    incident_id: str
    incident_type: Literal["medical", "security", "crowd_crush", "fire",
                             "infrastructure", "weather"]
    severity: Literal["minor", "moderate", "major", "critical"]
    zone_id: str
    description: str
    responding_staff: list[str]
    external_services_notified: list[str]
    status: Literal["reported", "responding", "contained", "resolved"]
    created_at: datetime
    resolved_at: Optional[datetime]

# Attendee chat session
class AttendeeSession(BaseModel):
    attendee_id: str
    ticket_id: str
    seat_location: SeatLocation
    accessibility_needs: list[str]
    food_orders: list[FoodOrder]
    conversation_history: list[dict]  # Claude messages format
    language_preference: str
```

---

## Prompt Caching Strategy

| Tier | Content | TTL | Who Uses It |
|---|---|---|---|
| 1 | Base venue context (~4K tokens: layout, zones, procedures) | 1 hour | All agents |
| 2 | Tool definitions (sorted deterministically by name) | 5 min | All agents |
| 3 | Conversation history (last assistant turn cached incrementally) | 5 min | AttendeeExperienceAgent |
| 4 | Emergency protocols reference (~3K tokens) | 1 hour | EmergencyResponseAgent |

**Rule:** `cache_control: {type: ephemeral}` placed on the **last block of the stable prefix only**. Dynamic content (timestamps, live occupancy, UUIDs) lives exclusively **after** the breakpoint — never before.

**Silent invalidators (prohibited before any cache breakpoint):**
- `datetime.now()` or `time.time()`
- Per-request UUIDs or event IDs
- `json.dumps()` without `sort_keys=True`
- Conditional prompt sections that vary per request

---

## Project Directory Structure

```
d:/APL/ch1/
├── PLAN.md                            ← this file
├── main.py                            # Production entry point
├── requirements.txt
├── pyproject.toml
├── .env.example
│
├── config/
│   ├── settings.py                    # Pydantic Settings + env vars
│   ├── venue_layout.json              # Static venue map, zones, gate IDs
│   └── agent_config.yaml
│
├── core/
│   ├── client.py                      # Anthropic client factory (singleton)
│   ├── event_bus.py                   # Async pub/sub (asyncio.Queue + Redis)
│   ├── state_store.py                 # Redis-backed shared venue state
│   ├── cache_manager.py              # Cache breakpoint helpers
│   └── streaming.py                  # WebSocket streaming bridge
│
├── agents/
│   ├── base_agent.py                  # Shared agentic loop (all agents inherit)
│   ├── orchestrator/
│   │   ├── agent.py
│   │   ├── system_prompt.py
│   │   ├── router.py                  # Event classification → agent routing
│   │   └── tools.py
│   ├── crowd_flow/
│   ├── wait_time/
│   ├── staff_coordination/
│   ├── emergency_response/
│   ├── attendee_experience/
│   ├── parking_transport/
│   ├── infrastructure_monitor/
│   └── analytics_insight/
│   (each sub-folder: agent.py · system_prompt.py · tools.py)
│
├── tools/
│   ├── registry.py                    # Tool schema registry + dispatcher
│   ├── simulators.py                  # Stub backends for all tools
│   ├── sensors/
│   ├── notifications/                 # Push, PA, digital signage
│   ├── venue_control/                 # Gates, parking, staff dispatch
│   └── external/                      # EMS/police/fire, transit feeds
│
├── api/
│   ├── main.py                        # FastAPI app + lifespan
│   ├── websocket_manager.py
│   └── routes/
│       ├── events.py                  # POST /events/sensor, /events/incident
│       ├── attendee.py                # WebSocket /ws/attendee/{id}
│       ├── operations.py             # GET /ops/dashboard, /ops/status
│       └── admin.py                   # POST /admin/mode, /admin/override
│
├── data/
│   ├── models.py                      # All Pydantic models
│   └── schemas/
│       ├── events.py
│       ├── venue.py
│       └── agent_io.py
│
├── prompts/
│   ├── base_venue_context.txt         # ~4K tokens, static (cached tier 1)
│   ├── emergency_protocol.txt         # ~3K tokens, static (cached tier 4)
│   └── attendee_persona.txt
│
├── tests/
│   ├── unit/
│   │   ├── test_tools.py
│   │   ├── test_routing.py
│   │   ├── test_cache_manager.py
│   │   └── test_data_models.py
│   ├── integration/
│   │   ├── test_crowd_flow_agent.py
│   │   ├── test_orchestrator_routing.py
│   │   ├── test_emergency_scenario.py
│   │   └── test_attendee_chat.py
│   └── scenarios/
│       ├── scenario_normal_operations.py
│       ├── scenario_crowd_surge.py
│       ├── scenario_medical_emergency.py
│       └── scenario_post_game_exit.py
│
└── scripts/
    ├── run_dev.py
    ├── simulate_event.py              # Feed synthetic sensor data
    └── load_venue_layout.py           # Init Redis with venue geometry
```

---

## Event Trigger Map

| Trigger | Source | Endpoint | Agents Activated |
|---|---|---|---|
| IoT density spike | Sensor network | `POST /events/sensor` | CrowdFlowAgent |
| Power/HVAC anomaly | BMS | `POST /events/sensor` | InfrastructureMonitorAgent |
| Medical incident | Staff report | `POST /events/incident` | EmergencyResponse + StaffCoordination |
| Attendee chat | Mobile app | `WS /ws/attendee/{id}` | AttendeeExperienceAgent |
| 30-second poll | Internal cron | Event bus tick | All agents (status snapshot) |
| Venue mode change | Admin | `POST /admin/mode` | All agents (mode transition) |
| Post-game timer | Scheduler | Event bus | Parking + CrowdFlow (exit surge) |

---

## Core Agentic Loop Pattern

```python
# agents/base_agent.py — inherited by all 9 agents

class BaseAgent:
    async def invoke(self, task: str, venue_state: VenueState, stream=False):
        system = build_system_prompt(self.name, venue_state)   # cache_control applied here
        messages = [{"role": "user", "content": task}]

        while True:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system,
                tools=self.tools,          # tool definitions pre-cached
                messages=messages,
            )

            if response.stop_reason == "end_turn":
                return self._extract_response(response)

            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                tool_results = await self._execute_tools(response.content)
                messages.append({"role": "user", "content": tool_results})
```

Streaming variant used for: **AttendeeExperienceAgent** (WebSocket chat) and **EmergencyResponseAgent** (PA announcement generation begins before full response is complete).

---

## Implementation Sequence

| Phase | Week | Deliverables |
|---|---|---|
| **Foundation** | 1 | `core/`, `data/models.py`, `config/`, `tools/simulators.py` |
| **Pilot Agents** | 2 | CrowdFlowAgent + AttendeeExperienceAgent with streaming, caching, unit tests |
| **Orchestration** | 3 | VenueOrchestrator, EventBus, FastAPI routes, routing integration tests |
| **Domain Agents** | 4 | WaitTime, StaffCoordination, Parking, Infrastructure agents |
| **Safety-Critical** | 5 | EmergencyResponseAgent (Opus, streaming PA, evacuation routing), scenario tests |
| **Intelligence** | 6 | AnalyticsInsightAgent, load testing, cache tuning, production config |

---

## Verification Plan

### Unit Tests
- Tool handlers tested in isolation against stubs
- Orchestrator routing assertions per event type and severity
- Cache breakpoint placement — dynamic content never before breakpoint
- Pydantic model validation with boundary inputs

### Integration Tests
- `test_crowd_surge` — CrowdFlowAgent calls `redirect_signage` + `notify_usher_team` when density > 85%
- `test_medical_routing` — Orchestrator routes `severity=critical` medical event to EmergencyResponseAgent
- `test_evacuation_order` — tool call sequence validated: `get_evacuation_route_status` → `trigger_evacuation` (never reversed)
- `test_attendee_streaming` — streaming + tool use verified in conversational agent

### Scenario Tests
- `scenario_crowd_surge` — 15 min rising density → signage + gates + ushers in correct sequence
- `scenario_medical_emergency` — EMS contacted, NIMS-format PA generated, no false evacuation
- `scenario_post_game_exit` — staggered section exits, extra shuttles dispatched, rideshare zone expanded
- `scenario_normal_operations` — all agents respond < 10s, cache hit rate > 0 on second requests

### Cache Validation
Every integration test asserts `cache_read_input_tokens >= 1000` on warm (second+) requests to confirm the prefix cache is functioning.

---

## Technology Stack

| Layer | Technology |
|---|---|
| AI / Agents | Anthropic Python SDK, Claude claude-opus-4-7 + claude-sonnet-4-6 |
| API Server | FastAPI + Uvicorn |
| Real-time | WebSockets (native FastAPI) |
| State Store | Redis (venue state, session data) |
| Event Bus | asyncio.Queue + Redis Pub/Sub |
| Data Models | Pydantic v2 |
| Testing | pytest + pytest-asyncio |
| Config | python-dotenv + Pydantic Settings |

---

*Ready for Q&A and implementation.*
