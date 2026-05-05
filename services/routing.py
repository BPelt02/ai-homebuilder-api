def route_lead(lead_data):
    priority = lead_data["qualification"]["priority"]

    if priority == "high":
        action = "SEND_TO_JOBTREAD"
    elif priority == "medium":
        action = "FOLLOW_UP_EMAIL"
    else:
        action = "LOW_PRIORITY_QUEUE"

    return {
        "action": action,
        "priority": priority
    }