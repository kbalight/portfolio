from fastapi import APIRouter
from pydantic import BaseModel
import os
from openai import OpenAI

router = APIRouter()


class TodoRequest(BaseModel):
    description: str

@router.post("/todo")
def create_todo_list(req: TodoRequest):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You create concise, actionable to-do lists."},
            {"role": "user", "content": f"Create a to-do list for: {req.description}"}
        ]
    )
    return {"tasks": response.choices[0].message["content"]}
