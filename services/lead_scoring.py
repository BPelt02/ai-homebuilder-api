def score_lead(lead):
    score = 0
    message = lead.message.lower()

    if "southlake" in message:
        score += 30
    if "custom home" in message or "build" in message:
        score += 30
    if "budget" in message or "$" in message:
        score += 20
    if lead.email:
        score += 10
    if lead.phone:
        score += 10

    if score >= 70:
        priority = "high"
    elif score >= 40:
        priority = "medium"
    else:
        priority = "low"

    return {
        "score": score,
        "priority": priority
    }