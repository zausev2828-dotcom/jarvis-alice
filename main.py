from fastapi import FastAPI, Request
import os
import requests

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@app.post("/")
async def alice(request: Request):
    data = await request.json()

    user_text = data.get("request", {}).get("original_utterance", "").strip()

    if not user_text:
        user_text = "Привет"

    try:
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-5.6-sol",
                "instructions": (
                    "Ты Джарвис — персональный голосовой помощник. "
                    "Отвечай только на русском языке. "
                    "Говори кратко, спокойно, уверенно и интеллигентно. "
                    "Стиль — футуристический персональный помощник."
                ),
                "input": user_text,
            },
            timeout=4,
        )

        if response.status_code != 200:
            print("OPENAI ERROR:", response.status_code, response.text)

            return {
                "version": "1.0",
                "response": {
                    "text": "Сэр, система временно недоступна.",
                    "tts": "Сэр, система временно недоступна.",
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

    except Exception as e:
        print("BACKEND ERROR:", repr(e))

        return {
            "version": "1.0",
            "response": {
                "text": "Сэр, произошла ошибка системы.",
                "tts": "Сэр, произошла ошибка системы.",
                "end_session": False,
            },
        }


@app.get("/")
async def health():
    return {"status": "Jarvis is online"}
