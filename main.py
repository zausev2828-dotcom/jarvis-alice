from fastapi import FastAPI, Request
import os
import requests

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@app.post("/")
async def alice(request: Request):
    data = await request.json()

    user_text = data.get("request", {}).get("original_utterance", "")

    if not user_text:
        user_text = "Привет"

    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-5.6",
            "input": [
                {
                    "role": "system",
                    "content": (
                        "Ты Джарвис. Отвечай пользователю на русском языке. "
                        "Говори спокойно, интеллигентно и уверенно, "
                        "в стиле футуристического персонального помощника."
                    ),
                },
                {
                    "role": "user",
                    "content": user_text,
                },
            ],
        },
        timeout=4,
    )

    if response.status_code != 200:
        return {
            "version": "1.0",
            "response": {
                "text": "Произошла ошибка при обращении к системе.",
                "end_session": False,
            },
        }

    result = response.json()
    answer = result.get("output_text", "Не удалось получить ответ.")

    return {
        "version": "1.0",
        "response": {
            "text": answer[:1024],
            "tts": answer[:1024],
            "end_session": False,
        },
    }


@app.get("/")
async def health():
    return {"status": "Jarvis is online"}
