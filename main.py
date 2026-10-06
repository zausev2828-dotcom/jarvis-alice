from fastapi import FastAPI, Request
import os
import requests

app = FastAPI()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


@app.post("/")
async def alice(request: Request):
    data = await request.json()

    user_text = data.get("request", {}).get("original_utterance", "").strip()

    if not user_text:
        user_text = "Привет"

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Ты Джарвис — персональный голосовой помощник. "
                            "Отвечай только на русском языке. "
                            "Говори кратко, спокойно, уверенно и интеллигентно. "
                            "Стиль — футуристический персональный помощник."
                        ),
                    },
                    {
                        "role": "user",
                        "content": user_text,
                    },
                ],
            },
            timeout=8,
        )

        if response.status_code != 200:
            print("GROQ ERROR:", response.status_code, response.text)

            return {
                "version": "1.0",
                "response": {
                    "text": "Сэр, система временно недоступна.",
                    "tts": "Сэр, система временно недоступна.",
                    "end_session": False,
                },
            }

        result = response.json()
        answer = result["choices"][0]["message"]["content"]

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
