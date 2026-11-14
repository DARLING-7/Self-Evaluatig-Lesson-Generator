import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

_API_KEY = os.getenv("GEMINI_API_KEY")
_models_raw = os.getenv("GEMINI_MODELS") or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MODELS = [m.strip() for m in _models_raw.split(",") if m.strip()]

if not _API_KEY or _API_KEY == "paste_your_key_here":
    raise RuntimeError("GEMINI_API_KEY is missing. Add your key to the .env file.")

_client = genai.Client(
    api_key=_API_KEY,
    http_options=types.HttpOptions(api_version="v1beta"),
)


def _is_daily_quota(error_text):
    t = error_text.lower()
    return "perday" in t or "per day" in t


def _is_temporary(error_text):
    markers = ["429", "500", "503", "504", "resource_exhausted",
               "unavailable", "deadline", "timed out", "connection"]
    return any(m in error_text.lower() for m in markers)


def call_gemini(prompt, temperature=0.7, json_mode=False, max_attempts=4):
    """Call Gemini. Retries temporary errors. Moves to the next model if the
    daily quota is used up or the model name is invalid."""
    config = types.GenerateContentConfig(
        temperature=temperature,
        response_mime_type="application/json" if json_mode else "text/plain",
    )
    last_error = None
    for model in MODELS:
        for attempt in range(1, max_attempts + 1):
            try:
                response = _client.models.generate_content(
                    model=model, contents=prompt, config=config
                )
                if response.text:
                    return response.text
                last_error = "Empty response from model"
            except Exception as e:
                last_error = str(e)
                if _is_daily_quota(last_error):
                    print(f"  [llm] Daily quota used up for {model}. Trying next model...")
                    break
                if not _is_temporary(last_error):
                    print(f"  [llm] {model} failed: {last_error[:120]}. Trying next model...")
                    break
            wait = 2 ** attempt
            print(f"  [llm] {model} attempt {attempt} failed ({last_error[:80]}). Retrying in {wait}s...")
            time.sleep(wait)
    raise RuntimeError(
        f"All models failed. Last error: {last_error[:300]}\n"
        "If this is a daily quota error, wait for the reset, switch model, or enable billing."
    )


def strip_fences(text):
    """Remove ```markdown or ```json fences if the model adds them."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text