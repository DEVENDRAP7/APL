from fastapi import APIRouter
from core.state_store import state_store

router = APIRouter(prefix="/ops", tags=["operations"])


@router.get("/status")
async def venue_status():
    state = state_store.get_state()
    return {
        "mode": state.operational_mode,
        "alert_level": state.overall_alert_level,
        "active_incidents": len(state.active_incidents),
        "zones": {
            zid: {
                "name": z.name,
                "occupancy_pct": round(z.occupancy_pct, 1),
                "queue_depth": z.queue_depth,
                "alert_level": z.alert_level,
            }
            for zid, z in state.zones.items()
        },
        "timestamp": state.timestamp.isoformat(),
    }
