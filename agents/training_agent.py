# agents/training_agent.py
import os
import json

FILE = "training_links.json"

def load_training_links():
    if os.path.exists(FILE):
        return set(json.load(open(FILE)))
    return set()

def save_training_links(links):
    all_links = load_training_links().union(links)
    json.dump(list(all_links), open(FILE, "w"))
