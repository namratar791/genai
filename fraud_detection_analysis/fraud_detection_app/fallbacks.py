# fallbacks.py

def behavior_fallback() -> dict:
    return {
        "agent": "behavior_agent",
        "fallback": True,
        "risk_score": 0.60,
        "confidence_score": 0.55,
        "issues": ["behavior agent unavailable"],
        "status_message": "Behavior Agent timeout. Conservative fallback applied.",
        "handoff_to": "orchestrator",
        "ui_events": [
            {
                "event_type": "agent_result",
                "agent": "behavior_agent",
                "status": "completed",
                "message": "Behavior Agent timeout. Conservative fallback applied.",
                "confidence_score": 0.55,
                "issues": ["behavior agent unavailable"],
                "handoff_to": "orchestrator",
            }
        ],
    }


def location_fallback() -> dict:
    return {
        "agent": "location_agent",
        "fallback": True,
        "risk_score": 0.65,
        "confidence_score": 0.60,
        "issues": ["location agent unavailable"],
        "geo_mismatch": None,
        "status_message": "Location Agent timeout. Conservative fallback applied.",
        "handoff_to": "orchestrator",
        "ui_events": [
            {
                "event_type": "agent_result",
                "agent": "location_agent",
                "status": "completed",
                "message": "Location Agent timeout. Conservative fallback applied.",
                "confidence_score": 0.60,
                "issues": ["location agent unavailable"],
                "handoff_to": "orchestrator",
            }
        ],
    }


def merchant_fallback() -> dict:
    return {
        "agent": "merchant_agent",
        "fallback": True,
        "risk_score": 0.60,
        "confidence_score": 0.58,
        "issues": ["merchant agent unavailable"],
        "status_message": "Merchant Agent timeout. Conservative fallback applied.",
        "handoff_to": "orchestrator",
        "ui_events": [
            {
                "event_type": "agent_result",
                "agent": "merchant_agent",
                "status": "completed",
                "message": "Merchant Agent timeout. Conservative fallback applied.",
                "confidence_score": 0.58,
                "issues": ["merchant agent unavailable"],
                "handoff_to": "orchestrator",
            }
        ],
    }


def device_fallback() -> dict:
    return {
        "agent": "device_agent",
        "fallback": True,
        "risk_score": 0.70,
        "confidence_score": 0.60,
        "issues": ["device agent unavailable"],
        "status_message": "Device Agent timeout. Conservative fallback applied.",
        "handoff_to": "orchestrator",
        "ui_events": [
            {
                "event_type": "agent_result",
                "agent": "device_agent",
                "status": "completed",
                "message": "Device Agent timeout. Conservative fallback applied.",
                "confidence_score": 0.60,
                "issues": ["device agent unavailable"],
                "handoff_to": "orchestrator",
            }
        ],
    }


def vpn_fallback() -> dict:
    return {
        "agent": "vpn_agent",
        "fallback": True,
        "risk_score": 0.68,
        "confidence_score": 0.59,
        "issues": ["vpn agent unavailable"],
        "status_message": "VPN Agent timeout. Conservative fallback applied.",
        "handoff_to": "orchestrator",
        "ui_events": [
            {
                "event_type": "agent_result",
                "agent": "vpn_agent",
                "status": "completed",
                "message": "VPN Agent timeout. Conservative fallback applied.",
                "confidence_score": 0.59,
                "issues": ["vpn agent unavailable"],
                "handoff_to": "orchestrator",
            }
        ],
    }


def policy_fallback() -> dict:
    return {
        "risk_score": 0.75,
        "confidence_score": 0.55,
        "risk_level": "medium",
        "issues": ["policy synthesis fallback applied"],
        "status_message": (
            "Policy synthesis fallback applied. Conservative fraud assessment generated."
        ),
        "ui_events": [
            {
                "event_type": "agent_result",
                "agent": "policy_node",
                "status": "completed",
                "message": "Policy synthesis fallback applied. Conservative fraud assessment generated.",
                "confidence_score": 0.55,
                "issues": ["policy synthesis fallback applied"],
                "handoff_to": "confidence_node",
            }
        ],
    }


def confidence_fallback() -> dict:
    return {
        "confidence_score": 0.45,
        "status_message": (
            "Confidence fallback applied. Reduced confidence due to incomplete or degraded analysis."
        ),
        "ui_events": [
            {
                "event_type": "agent_result",
                "agent": "confidence_node",
                "status": "completed",
                "message": "Confidence fallback applied. Reduced confidence due to incomplete or degraded analysis.",
                "confidence_score": 0.45,
                "handoff_to": "action_agent",
            }
        ],
    }


def action_fallback() -> dict:
    return {
        "final_action": "ESCALATE",
        "final_confidence": 0.55,
        "risk_level": "high",
        "reason": "Conservative fallback applied due to action processing failure.",
        "status_message": "Action fallback applied. Recommended action: ESCALATE.",
        "requires_human_review": False,
        "ui_events": [
            {
                "event_type": "final_response",
                "agent": "action_agent",
                "status": "completed",
                "message": "Action fallback applied. Recommended action: ESCALATE.",
                "final_action": "ESCALATE",
                "final_confidence": 0.55,
                "handoff_to": "guardrail_node",
            }
        ],
    }


def guardrail_fallback() -> dict:
    return {
        "validated_action": "REVIEW",
        "adjusted": True,
        "adjustment_reason": "Guardrail fallback applied. Routing to human review conservatively.",
        "ui_events": [
            {
                "event_type": "agent_result",
                "agent": "guardrail_node",
                "status": "completed",
                "message": "Guardrail fallback applied. Routing to human review conservatively.",
                "handoff_to": "hil_node",
            }
        ],
    }


def hil_fallback() -> dict:
    return {
        "review_required": True,
        "review_reason": "Human review fallback applied due to insufficient automation confidence.",
        "analyst_summary": (
            "Automated analysis could not complete with sufficient confidence. "
            "Please review transaction risk signals manually."
        ),
        "ui_events": [
            {
                "event_type": "agent_result",
                "agent": "hil_node",
                "status": "completed",
                "message": "Human review package prepared using fallback summary.",
                "handoff_to": "finalize_node",
            }
        ],
    }