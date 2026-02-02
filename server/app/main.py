import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise RuntimeError("GROQ_API_KEY not set")

client = None

def get_client():
    global client
    if client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set. Please set it in your environment variables (`.env file`).")
        client = Groq(api_key=api_key)
    return client

app = FastAPI(title="Written Feedback Interpretation API")


class InterpretRequest(BaseModel):
    text: str
    options: dict


class InterpretResponse(BaseModel):
    output: str


def build_system_prompt(options: dict) -> str:
    goals = []
    if options.get("simplify"):
        goals.append("Simplify the language while preserving meaning.")
    if options.get("soften"):
        goals.append("Soften the tone to be constructive and supportive.")
    if options.get("caseSupport"):
        goals.append("Add brief case support: 2–4 bullet points suggesting concrete examples/evidence.")

    goals_text = "\n".join(f"- {g}" for g in goals) or "- Return the original feedback unchanged."

    return f"""
You are assisting professors and teaching assistants in rewriting written feedback.

Goals:
{goals_text}

Return ONLY the rewritten feedback text. Do not add explanations.
""".strip()


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/interpret", response_model=InterpretResponse)
def interpret(req: InterpretRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Input text is empty")

    system_prompt = build_system_prompt(req.options)

    try:
        # Groq chat completions (OpenAI-compatible)
        client = get_client()
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.text},
            ],
            temperature=0.2,
        )
        output = resp.choices[0].message.content or ""
        return InterpretResponse(output=output)

    except Exception as e:
        # Surface a useful error message in logs
        print("Groq error:", repr(e))
        raise HTTPException(status_code=500, detail="Groq request failed")
