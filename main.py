from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import json
import requests

from services.lead_scoring import score_lead
from services.events import log_event
from services.routing import route_lead
from services.jobtread import sync_lead_to_jobtread
from agents.lead_intelligence import analyze_lead_with_agent


ZAPIER_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/27469070/4yhg2io/"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pelthomes.com",
        "https://www.pelthomes.com",
        "https://euphonious-platypus-359667.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Lead(BaseModel):
    name: str
    phone: str | None = None
    email: str | None = None
    message: str


@app.get("/")
def home():
    return {"status": "API running"}


@app.post("/lead")
def create_lead(lead: Lead):
    lead_data = lead.dict()
    lead_data["created_at"] = datetime.now().isoformat()

    # Score lead
    lead_data["qualification"] = score_lead(lead)

    # Route lead
    route = route_lead(lead_data)
    lead_data["route"] = route

    # Agent analysis
    try:
        lead_data["agent_analysis"] = analyze_lead_with_agent(lead_data)
    except Exception as e:
        lead_data["agent_analysis"] = {
            "error": str(e),
            "recommendation": "Manual follow-up required",
            "next_question": "What timeline are they hoping to build within?"
        }

    # Send to Zapier email alert webhook
    try:
        zapier_response = requests.post(
            ZAPIER_WEBHOOK_URL,
            json=lead_data,
            timeout=10
        )

        lead_data["zapier_alert"] = {
            "status_code": zapier_response.status_code,
            "success": zapier_response.status_code in [200, 201, 202]
        }

    except Exception as e:
        lead_data["zapier_alert"] = {
            "success": False,
            "error": str(e)
        }

    # Sync to JobTread / Zapier / CRM
    try:
        jobtread_sync = sync_lead_to_jobtread(lead_data)
    except Exception as e:
        jobtread_sync = {"error": str(e)}

    lead_data["jobtread_sync"] = jobtread_sync

    # Log event
    try:
        event = log_event("NEW_LEAD", {
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "priority": lead_data["qualification"].get("priority"),
            "score": lead_data["qualification"].get("score"),
            "action": route.get("action"),
            "agent_recommendation": lead_data["agent_analysis"].get("recommendation"),
            "next_question": lead_data["agent_analysis"].get("next_question"),
            "zapier_alert_success": lead_data["zapier_alert"].get("success")
        })
    except Exception as e:
        event = {"error": str(e)}

    # Store lead locally
    try:
        with open("leads.json", "a") as f:
            f.write(json.dumps(lead_data) + "\n")
    except Exception as e:
        lead_data["local_storage_error"] = str(e)

    return {
        "status": "lead stored",
        "lead": lead_data,
        "event": event,
        "jobtread_sync": jobtread_sync,
        "zapier_alert": lead_data["zapier_alert"]
    }