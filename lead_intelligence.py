def analyze_lead_with_agent(lead_data):
    message = lead_data.get("message", "").lower()
    score = lead_data["qualification"]["score"]

    if score >= 70:
        recommendation = "Call immediately and offer a private consultation."
    elif score >= 40:
        recommendation = "Send a follow-up email asking about budget, timeline, and lot status."
    else:
        recommendation = "Keep in nurture. Do not prioritize."

    if "lot" in message:
        next_question = "Do they already own the lot, or are they still searching?"
    elif "budget" not in message and "$" not in message:
        next_question = "What budget range are they targeting?"
    else:
        next_question = "What timeline are they hoping to build within?"

    return {
        "agent": "lead_intelligence",
        "recommendation": recommendation,
        "next_question": next_question
    }