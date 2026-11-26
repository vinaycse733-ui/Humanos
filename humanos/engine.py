"""Local Ollama inference; no cloud fallback."""
import json
import http.client

def ask(prompt: str, model: str = "llama3.2") -> str:
    if not prompt.strip() or not model.strip():
        raise ValueError("Prompt and model must not be empty")
    conn = http.client.HTTPConnection("127.0.0.1", 11434, timeout=120)
    try:
        conn.request("POST", "/api/generate", json.dumps({"model": model, "prompt": prompt, "stream": False}), {"Content-Type": "application/json"})
        response = conn.getresponse()
        if response.status != 200:
            raise RuntimeError(f"Local model returned HTTP {response.status}")
        data = json.loads(response.read(8 * 1024 * 1024))
        if not isinstance(data.get("response"), str):
            raise RuntimeError("Invalid model response")
        return data["response"]
    finally:
        conn.close()
