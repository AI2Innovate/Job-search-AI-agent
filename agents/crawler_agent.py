# agents/crawler_agent.py
import requests
import os
import json

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")

def propose_additional_queries(keywords, existing_queries, model="mistral"):
    prompt = f"Given keywords: {keywords} and queries: {existing_queries}, suggest 4 more queries."
    try:
        resp = requests.post(f"{OLLAMA_HOST}/api/generate",
                             json={"model": model, "prompt": prompt, "stream": False},
                             timeout=30)
        qs = json.loads(resp.json().get("response", "[]"))
        return [q for q in qs if isinstance(q, str)]
    except Exception as e:
        print("Additional query generation failed:", e)
        return []
