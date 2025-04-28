# app.py - Self-Training v4 Complete (Fixed Full)

import streamlit as st
import json, os
import urllib.parse
from agents.search_agent import generate_search_queries, search_jobs
from agents.crawler_agent import propose_additional_queries
from agents.portal_agent import update_portals
from agents.training_agent import save_training_links, load_training_links
from agents.scraper_agent import scrape_job_post
from agents.resume_parser import (
    extract_text_from_pdf, extract_text_from_docx,
    extract_keywords_from_text, extract_keywords_from_csv
)

HISTORY_FILE = "chat_history.json"
BOOKMARKS_FILE = "bookmarks.json"
TRAINING_FILE = "training_links.json"

PORTAL_TEMPLATES = {
    "indeed.com": "https://www.indeed.com/jobs?q={}",
    "monster.com": "https://www.monster.com/jobs/search/?q={}",
    "glassdoor.com": "https://www.glassdoor.com/Job/jobs.htm?sc.keyword={}",
    "linkedin.com": "https://www.linkedin.com/jobs/search?keywords={}",
    "simplyhired.com": "https://www.simplyhired.com/search?q={}",
    "careerbuilder.com": "https://www.careerbuilder.com/jobs?keywords={}",
}

st.set_page_config(page_title="AI Job Searcher Chat", layout="wide")
st.title("🕵️ AI Job Searcher Chat (v4 Complete)")

# Initialize state
if "messages" not in st.session_state:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            st.session_state.messages = json.load(f)
    else:
        st.session_state.messages = [{"role":"assistant","content":"Hello! Upload CV or ask a query."}]
        with open(HISTORY_FILE, "w") as f:
            json.dump(st.session_state.messages, f)
    st.session_state.cv_keywords = None

# Known jobs for deduplication
if os.path.exists(TRAINING_FILE):
    with open(TRAINING_FILE, "r") as f:
        st.session_state.known_jobs = set(json.load(f))
else:
    st.session_state.known_jobs = set()

# Bookmarks
if "bookmarks" not in st.session_state:
    if os.path.exists(BOOKMARKS_FILE):
        with open(BOOKMARKS_FILE, "r") as f:
            st.session_state.bookmarks = set(json.load(f))
    else:
        st.session_state.bookmarks = set()

# Save utilities
def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(st.session_state.messages, f)

def save_bookmarks():
    with open(BOOKMARKS_FILE, "w") as f:
        json.dump(list(st.session_state.bookmarks), f)

def save_training_links(links):
    updated = st.session_state.known_jobs.union(links)
    with open(TRAINING_FILE, "w") as f:
        json.dump(list(updated), f)
    st.session_state.known_jobs = updated

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})
    save_history()

# Sidebar bookmarks
st.sidebar.header("🔖 Bookmarks")
if st.session_state.bookmarks:
    for url in st.session_state.bookmarks:
        st.sidebar.markdown(f"- [{url}]({url})")
    if st.sidebar.button("Clear All Bookmarks"):
        st.session_state.bookmarks.clear()
        save_bookmarks()
        st.experimental_rerun()
else:
    st.sidebar.write("No bookmarks yet.")

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Generate clickable query links
def generate_query_links(queries):
    links = []
    for q in queries:
        encoded = urllib.parse.quote(q)
        for template in PORTAL_TEMPLATES.values():
            links.append(template.format(encoded))
    return list(dict.fromkeys(links))

# CV uploader
uploaded = st.file_uploader("Upload CV (PDF/CSV/DOCX)", type=["pdf","csv","docx"])
if uploaded and st.session_state.cv_keywords is None:
    try:
        name = uploaded.name.lower()
        if name.endswith(".pdf"):
            text = extract_text_from_pdf(uploaded)
        elif name.endswith(".csv"):
            text = extract_keywords_from_csv(uploaded)
        else:
            text = extract_text_from_docx(uploaded)
        keywords = extract_keywords_from_text(text)
        st.session_state.cv_keywords = keywords
        add_message("assistant", f"Extracted CV summary: {keywords}")
    except Exception as e:
        st.toast(f"Error extracting CV: {e}")
        keywords = ""

    # Query generation
    queries = generate_search_queries(keywords)
    extra = propose_additional_queries(keywords, queries)
    all_q = list(dict.fromkeys([q for q in queries if isinstance(q, str)] + [q for q in extra if isinstance(q, str)]))
    links = generate_query_links(all_q)
    add_message("assistant", "**🔗 Generated Query Links:**")
    st.chat_message("assistant").markdown("\n".join(f"- [{u}]({u})" for u in links))

    # Search & scrape
    urls = []
    for q in all_q:
        urls.extend(search_jobs(q))
    update_portals(urls)
    new_urls = [u for u in urls if u not in st.session_state.known_jobs]
    save_training_links(new_urls)
    # Updated Bookmark Button Functionality
    for u in new_urls[:5]:
        job = scrape_job_post(u)
        with st.chat_message("assistant"):
            st.markdown(f"**{job['title']}**  \n{job['url']}")
            if st.button("Bookmark", key=f"bm3_{u}"):
                # Update bookmarks without refreshing the page
                st.session_state.bookmarks.add(u)
                save_bookmarks()
                st.toast("Bookmark added successfully!")

# Manual Search Panel
with st.expander("🔎 Manual Job Search"):
    role = st.text_input("Role", key="role_input")
    exp = st.text_input("Experience", key="exp_input")
    loc = st.text_input("Location", key="loc_input")
    job_type = st.selectbox("Type", ["", "Permanent", "Contract"], key="type_input")
    work_mode = st.selectbox("Work Mode", ["", "Hybrid", "Onsite", "Remote"], key="mode_input")
    days_limit = st.number_input("Posted Within Last (Days)", min_value=0, step=1, key="days_limit_input")

    if st.button("Search Jobs", key="manual_search_btn"):
        manual_q = " ".join(filter(None, [role, exp, loc, job_type, work_mode, f"Posted within last {days_limit} days" if days_limit > 0 else ""]))
        if st.session_state.cv_keywords:
            manual_q += " " + st.session_state.cv_keywords
        add_message("user", manual_q)

        queries = generate_search_queries(manual_q)
        extra = propose_additional_queries(manual_q, queries)
        all_q = list(dict.fromkeys([q for q in queries if isinstance(q, str)] + [q for q in extra if isinstance(q, str)]))
        links = generate_query_links(all_q)
        add_message("assistant", "**🔗 Generated Query Links:**")
        st.chat_message("assistant").markdown("\n".join(f"- [{u}]({u})" for u in links))

        urls = []
        for q in all_q:
            urls.extend(search_jobs(q))
        update_portals(urls)
        new_urls = [u for u in urls if u not in st.session_state.known_jobs]
        save_training_links(new_urls)
        for u in new_urls[:5]:
            job = scrape_job_post(u)
            with st.chat_message("assistant"):
                st.markdown(f"**{job['title']}**  \n{job['url']}")
                if st.button("Bookmark", key=f"bm2_{u}"):
                    st.session_state.bookmarks.add(u)
                    save_bookmarks()
                    st.experimental_rerun()

# Free-form Chat Input
user_input = st.chat_input("Type your job search query…")
if user_input:
    add_message("user", user_input)
    combined = user_input + (" " + st.session_state.cv_keywords if st.session_state.cv_keywords else "")
    
    # Generate queries for both job portals and general web search
    queries = generate_search_queries(combined)
    extra = propose_additional_queries(combined, queries)
    all_q = list(dict.fromkeys([q for q in queries if isinstance(q, str)] + [q for q in extra if isinstance(q, str)]))
    
    # Generate links for job portals
    portal_links = generate_query_links(all_q)
    
    # Perform a general web search for additional links
    general_links = []
    for q in all_q:
        general_links.extend(search_jobs(q))  # Assuming search_jobs can handle general web searches
    
    # Combine and display all links
    all_links = list(dict.fromkeys(portal_links + general_links))
    add_message("assistant", "**🔗 Generated Query Links:**")
    st.chat_message("assistant").markdown("\n".join(f"- [{u}]({u})" for u in all_links))

    # Update portals and save training links
    update_portals(general_links)
    new_urls = [u for u in general_links if u not in st.session_state.known_jobs]
    save_training_links(new_urls)
    for u in new_urls[:5]:
        job = scrape_job_post(u)
        with st.chat_message("assistant"):
            st.markdown(f"**{job['title']}**  \n{job['url']}")
            if st.button("Bookmark", key=f"bm3_{u}"):
                # Update bookmarks without refreshing the page
                st.session_state.bookmarks.add(u)
                save_bookmarks()
                st.toast("Bookmark added successfully!")
