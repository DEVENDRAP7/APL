import json
from core.client import get_client, build_cached_system, is_mock_mode
from agents.vision_anomaly.system_prompt import SYSTEM_PROMPT
from data.models import CameraFrame


class VisionAnomalyAgent:
    name = "vision_anomaly"
    model = "claude-sonnet-4-6"

    def __init__(self):
        self.client = get_client()

    async def analyse(self, frame: CameraFrame) -> dict:
        if is_mock_mode():
            return {
                "anomaly_detected": False,
                "confidence": 0.12,
                "description": "Normal crowd distribution. No anomalies detected.",
                "recommended_action": "Continue monitoring.",
                "demo_mode": True,
            }

        system = build_cached_system(SYSTEM_PROMPT)
        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            system=system,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": frame.frame_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            f"Camera: {frame.camera_id}, Zone: {frame.zone_id}. "
                            f"CV flags: {frame.cv_flags}. Anomaly score: {frame.anomaly_score:.2f}. "
                            "Analyse and respond in JSON."
                        ),
                    },
                ],
            }],
        )
        text = response.content[0].text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text, "parse_error": True}
