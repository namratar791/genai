def location_fallback() -> dict:
    return {
        "agent": "location_agent",
        "fallback": True,
        "risk_score": 0.60,
        "confidence_score": 0.55,
        "issues": ["location agent unavailable"],
        "status_message": "Location Agent timeout. Conservative fallback applied.",
        "handoff_to": "orchestrator",
        "ui_events": [
            {
                "event_type": "agent_result",
                "status": "completed",
                "message": "Location Agent timeout. Conservative fallback applied.",
                "confidence_score": 0.55,
                "issues": ["location agent unavailable"],
                "handoff_to": "orchestrator",
            }
        ],
        "completed": True,
        "needs_followup": False,
    }
