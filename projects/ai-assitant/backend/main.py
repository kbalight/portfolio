from auth.google import get_calendar_service
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
import os
from openai import OpenAI
from dotenv import load_dotenv

# Import routers
from todo.routes import router as todo_router
from schedule.routes import router as calendar_router

# Import OAuth flow from auth/google.py
from auth.google import flow

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/auth/login")
def login():
    authorization_url, _ = flow.authorization_url(prompt="consent")
    return RedirectResponse(authorization_url)
    
@app.get("/auth/callback")
def callback(request: Request):
    try:
        flow.fetch_token(authorization_response=str(request.url))
        credentials = flow.credentials

        # Save token.json
        token_data = {
            "client_id": flow.client_config["client_id"],
            "client_secret": flow.client_config["client_secret"],
            "refresh_token": credentials.refresh_token,
            "token": credentials.token,
            "type": "authorized_user"
        }

        with open("token.json", "w") as token_file:
            import json
            json.dump(token_data, token_file)

        return JSONResponse(token_data)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
        
@app.post("/calendar/create")
def create_event(event: dict):
    service = get_calendar_service()

    event_body = {
        "summary": event.get("summary"),
        "description": event.get("description"),
        "start": {
            "dateTime": event.get("start"),
            "timeZone": "America/New_York"
        },
        "end": {
            "dateTime": event.get("end"),
            "timeZone": "America/New_York"
        }
    }

    created_event = service.events().insert(
        calendarId="primary",
        body=event_body
    ).execute()

    return {"event_id": created_event.get("id")}
    
@app.get("/calendar/list")
def list_events():
    service = get_calendar_service()

    events = service.events().list(
        calendarId="primary",
        maxResults=10,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    return events.get("items", [])

@app.delete("/calendar/delete/{event_id}")
def delete_event(event_id: str):
    service = get_calendar_service()

    service.events().delete(
        calendarId="primary",
        eventId=event_id
    ).execute()

    return {"status": "deleted"}


class UserMessage(BaseModel):
    message: str

@app.post("/assistant")
def assistant(user_message: UserMessage):
    text = user_message.message

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
You are a scheduling assistant. ALWAYS respond in valid JSON only.

Possible intents:
- create_event
- delete_event
- list_events

For create_event, return:
{
  "intent": "create_event",
  "summary": "...",
  "description": "...",
  "start": "YYYY-MM-DDTHH:MM:SS",
  "end": "YYYY-MM-DDTHH:MM:SS"
}

For delete_event, return:
{
  "intent": "delete_event",
  "event_id": "..."
}

For list_events, return:
{
  "intent": "list_events"
}
"""
            },
            {"role": "user", "content": text}
        ]
    )

    import json
    intent_data = json.loads(response.choices[0].message.content)

    intent = intent_data["intent"]

    # CREATE EVENT
    if intent == "create_event":
        service = get_calendar_service()

        event_body = {
            "summary": intent_data["summary"],
            "description": intent_data["description"],
            "start": {"dateTime": intent_data["start"], "timeZone": "America/New_York"},
            "end": {"dateTime": intent_data["end"], "timeZone": "America/New_York"}
        }

        created = service.events().insert(calendarId="primary", body=event_body).execute()
        return {"assistant": "Event created", "event_id": created["id"]}

    # DELETE EVENT
    if intent == "delete_event":
        service = get_calendar_service()
        service.events().delete(calendarId="primary", eventId=intent_data["event_id"]).execute()
        return {"assistant": "Event deleted"}

    # LIST EVENTS
    if intent == "list_events":
        service = get_calendar_service()
        events = service.events().list(
            calendarId="primary",
            maxResults=10,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        return {"assistant": "Here are your events", "events": events.get("items", [])}

    return {"assistant": "I didn’t understand that request."}

