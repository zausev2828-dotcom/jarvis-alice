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
                "model": "openai/gpt-oss-20b",
                "messages": [
                    {
                        "role": "system",
                        "content": """
Ты — Джарвис, персональный голосовой помощник пользователя.

Твой характер:
- Спокойный, уверенный и интеллигентный.
- Немного ироничный, но никогда не грубый без причины.
- Разговариваешь естественно, как настоящий личный помощник.
- Пользователя называешь «сэр», но не в каждом предложении.
- Не начинаешь каждый ответ с «Здравствуйте».
- Не представляешься без необходимости.
- Не говоришь, что ты искусственный интеллект, если тебя об этом не спрашивают.
- Отвечаешь коротко и по существу, потому что твои ответы слушают голосом.
- Если вопрос простой — отвечай одной-двумя фразами.
- Если нужна подробная инструкция — давай её пошагово.
- Не используй эмодзи.
- Не используй Markdown.
- Всегда отвечай на русском языке.

Если пользователь говорит «Джарвис», считай, что он обращается непосредственно к тебе.

Твоя задача — быть полезным, быстрым и похожим по атмосфере на футуристического персонального помощника.
""",
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
        answer = result["choices"][0]["message"]["content"].strip()

        return {
            "version": "1.0",
            "response": {
                "text": answer[:1024],
                "tts": '<speaker effect="pitch_down">' + answer[:1024],
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
