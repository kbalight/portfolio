from fastapi import FastAPI
from pydantic import BaseModel
import os
from openai import OpenAI

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
