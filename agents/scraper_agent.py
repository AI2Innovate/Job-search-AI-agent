# agents/scraper_agent.py
import requests
from bs4 import BeautifulSoup

def scrape_job_post(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else url
        return {"url": url, "title": title}
    except Exception as e:
        return {"url": url, "title": url}
