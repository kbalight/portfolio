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

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/auth/login")
def login():
    authorization_url, _ = flow.authorization_url(prompt="consent")
    return RedirectResponse(authorization_url)
    
@app.get("/auth/callback")
def callback(request: Request):
    flow.fetch_token(authorization_response=str(request.url))

    credentials = flow.credentials

    return JSONResponse({
        "access_token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "id_token": credentials.id_token
    })

class UserMessage(BaseModel):
    message: str

@app.post("/assistant")
def assistant_endpoint(user: UserMessage):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful personal assistant."},
            {"role": "user", "content": user.message}
        ]
    )
    return {"reply": response.choices[0].message["content"]}

app.include_router(todo_router)
app.include_router(calendar_router)
