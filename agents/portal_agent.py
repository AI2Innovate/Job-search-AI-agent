# agents/portal_agent.py
import json
import os
import requests

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
PORTALS_FILE = "known_portals.json"

def load_portals():
    if os.path.exists(PORTALS_FILE):
        return set(json.load(open(PORTALS_FILE)))
    return set()

def save_portals(portals):
    json.dump(sorted(portals), open(PORTALS_FILE, "w"))

def is_job_portal(domain):
    prompt = f"Is {domain} primarily a job board? Yes or No."
    try:
        resp = requests.post(f"{OLLAMA_HOST}/api/generate",
                             json={"model":"mistral","prompt":prompt,"stream":False},
                             timeout=30)
        return resp.json().get("response","").strip().lower().startswith("y")
    except Exception as e:
        print("Ollama portal classification failed:", e)
        return False

def update_portals(urls):
    portals = load_portals()
    for u in urls:
        domain = requests.utils.urlparse(u).netloc
        if domain and domain not in portals:
            if is_job_portal(domain):
                portals.add(domain)
    save_portals(portals)
    return portals
