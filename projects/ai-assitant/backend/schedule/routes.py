from fastapi import APIRouter
from pydantic import BaseModel
import os
from openai import OpenAI

router = APIRouter()

class CalendarRequest(BaseModel):
    description: str

@router.post("/calendar")
def calendar_planner(req: CalendarRequest):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You create structured daily schedules and calendar plans."},
            {"role": "user", "content": f"Create a calendar plan for: {req.description}"}
        ]
    )
    return {"calendar_plan": response.choices[0].message["content"]}
