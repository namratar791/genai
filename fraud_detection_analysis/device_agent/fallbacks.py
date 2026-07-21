def device_fallback() -> dict:
    return {
        "agent": "device_agent",
        "fallback": True,
        "risk_score": 0.60,
        "confidence_score": 0.55,
        "issues": ["device agent unavailable"],
        "status_message": "Device Agent timeout. Conservative fallback applied.",
        "handoff_to": "orchestrator",
        "ui_events": [
            {
                "event_type": "agent_result",
                "status": "completed",
                "message": "Device Agent timeout. Conservative fallback applied.",
                "confidence_score": 0.55,
                "issues": ["device agent unavailable"],
                "handoff_to": "orchestrator",
            }
        ],
        "completed": True,
        "needs_followup": False,
    }
