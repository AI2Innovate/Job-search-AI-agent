# agents/search_agent.py
import requests
from duckduckgo_search import DDGS
import os
import json

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")

def generate_search_queries(keywords, model="mistral"):
    prompt = f"Generate 4 concise search queries for job postings matching these keywords: {keywords}"
    try:
        resp = requests.post(f"{OLLAMA_HOST}/api/generate",
                             json={"model": model, "prompt": prompt, "stream": False},
                             timeout=30)
        body = resp.json().get("response", "")
        queries = json.loads(body)
        return [q for q in queries if isinstance(q, str)]
    except Exception as e:
        print("Ollama query generation failed:", e)
        return [keywords]

def search_jobs(query, max_results=10):
    urls = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results, safesearch="Off", region="wt-wt"):
                href = r.get("href")
                if href:
                    urls.append(href)
    except Exception as e:
        print("DDGS search failed:", e)
    return urls
