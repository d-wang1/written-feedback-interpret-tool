import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
from app.prompt_cfg import prompt_store, build_system_prompt, build_user_prompt
from app.model_cfg import model_config_store

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


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/interpret", response_model=InterpretResponse)
def interpret(req: InterpretRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Input text is empty")

    try:
        # ----- Load prompt configuration -----
        prompt_cfg = prompt_store.load()
        system_prompt = build_system_prompt(prompt_cfg)
        user_prompt = build_user_prompt(req.text, req.options, prompt_cfg)

        # ----- Load model configuration -----
        model_cfg = model_config_store.load()
        generation = model_cfg.get("generation", {})

        model_name = model_cfg.get("model")
        temperature = generation.get("temperature", 0.2)
        top_p = generation.get("top_p", 1.0)
        max_tokens = generation.get("max_tokens", 512)
        stop = model_cfg.get("stop_sequences") or None

        # ----- Call Groq -----
        resp = get_client().chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stop=stop,
        )

        output = resp.choices[0].message.content or ""
        return InterpretResponse(output=output)

    except HTTPException:
        raise
    except Exception as e:
        print("interpret() error:", repr(e))
        raise HTTPException(status_code=500, detail="LLM request failed")
