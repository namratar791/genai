def vpn_fallback() -> dict:
    return {
        "agent": "vpn_agent",
        "fallback": True,
        "risk_score": 0.60,
        "confidence_score": 0.55,
        "issues": ["vpn agent unavailable"],
        "status_message": "VPN Agent timeout. Conservative fallback applied.",
        "handoff_to": "orchestrator",
        "ui_events": [
            {
                "event_type": "agent_result",
                "status": "completed",
                "message": "VPN Agent timeout. Conservative fallback applied.",
                "confidence_score": 0.55,
                "issues": ["vpn agent unavailable"],
                "handoff_to": "orchestrator",
            }
        ],
        "completed": True,
        "needs_followup": False,
    }
