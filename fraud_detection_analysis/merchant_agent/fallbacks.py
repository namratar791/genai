def merchant_fallback() -> dict:
    return {
        "agent": "merchant_agent",
        "fallback": True,
        "risk_score": 0.60,
        "confidence_score": 0.55,
        "issues": ["merchant agent unavailable"],
        "status_message": "Merchant Agent timeout. Conservative fallback applied.",
        "handoff_to": "orchestrator",
        "ui_events": [
            {
                "event_type": "agent_result",
                "status": "completed",
                "message": "Merchant Agent timeout. Conservative fallback applied.",
                "confidence_score": 0.55,
                "issues": ["merchant agent unavailable"],
                "handoff_to": "orchestrator",
            }
        ],
        "completed": True,
        "needs_followup": False,
    }
