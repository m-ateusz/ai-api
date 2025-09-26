import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import httpx

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

API_URL = "https://api.perplexity.ai/chat/completions"
API_KEY = os.getenv("PERPLEXITY_API_KEY")

@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/api")
async def ask_perplexity(text: str = Form(...)):
    if not API_KEY:
        return JSONResponse({"error": "Brak klucza API."}, status_code=500)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "You are a translation assistant. Translate everything to English, aiming to use natural idioms and advanced, native-like language."},
            {"role": "user", "content": text}
        ]
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(API_URL, headers=headers, json=payload)
            if r.status_code != 200:
                return JSONResponse({"error": "Błąd API Perplexity.", "details": r.text}, status_code=500)
            data = r.json()
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            urls = data.get("citations")
            return {
                "response": message.get("content", "Brak odpowiedzi."),
                "urls": urls
            }
    except Exception as e:
        return JSONResponse({"error": f"Błąd połączenia: {e}"}, status_code=500)
    except Exception as e:
        return JSONResponse({"error": f"Błąd API Perplexity: {e}"}, status_code=500)
