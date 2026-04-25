from data.models import CameraFrame


class VisionAnomalyAgent:
    name = "vision_anomaly"
    model = "antigravity-vision"

    def __init__(self):
        self.client = None

    async def analyse(self, frame: CameraFrame) -> dict:
        return {
            "anomaly_detected": False,
            "confidence": 0.12,
            "description": "Normal crowd distribution. No anomalies detected.",
            "recommended_action": "Continue monitoring.",
            "demo_mode": True,
        }
