## AI Job search Agent

# New Feature in progress development 
- promopt template for searching & scrape
- real and fake job posting list with links in a table format
- explain and build new features like cv parsing & look for exact job macthes


 AI-powered job search assistant with the following functionalities:

1. Job Search and Query Generation
Generate Search Queries: Uses keywords (e.g., from a CV or user input) to generate concise job search queries via the generate_search_queries function in search_agent.py.
Propose Additional Queries: Suggests more queries based on existing ones using the propose_additional_queries function in crawler_agent.py.
Search Jobs: Performs web searches for job postings using DuckDuckGo via the search_jobs function in search_agent.py.
2. Job Portal Management
Known Portals: Maintains a list of known job portals in known_portals.json.
Portal Classification: Determines if a domain is a job portal using the is_job_portal function in portal_agent.py.
Update Portals: Adds new job portals to the list after validation via the update_portals function in portal_agent.py.
3. Job Post Scraping
Scrape Job Details: Extracts job titles and URLs from job postings using the scrape_job_post function in scraper_agent.py.
4. CV Parsing
Extract Text: Reads text from uploaded CVs in PDF, DOCX, or CSV formats using functions in resume_parser.py.
Extract Keywords: Extracts key phrases from the CV text for query generation.
5. Training Links Management
Save Training Links: Stores job links for deduplication and training purposes in training_links.json via save_training_links in training_agent.py.
Load Training Links: Loads previously saved job links for deduplication.
6. Chat Interface
Chat History: Maintains a chat history in chat_history.json to display past interactions.
Free-form Chat: Allows users to input job search queries directly.
Manual Search Panel: Provides a form for users to specify job roles, experience, and location for manual searches.
7. Bookmarks
Save Bookmarks: Allows users to bookmark job postings, stored in bookmarks.json.
Manage Bookmarks: Displays and clears bookmarks via the sidebar.
8. Streamlit-based UI
The application is built using Streamlit, providing an interactive web interface for users to upload CVs, view job search results, and interact with the assistant.
9. Dockerized Deployment
The application is containerized using Docker, with a Dockerfile and docker-compose.yml for easy deployment.
10. Environment Configuration
Uses environment variables (e.g., OLLAMA_HOST) for API endpoints and configurations.
This codebase is designed to automate job searches, enhance user experience with AI-driven query generation, and provide a streamlined interface for job seekers.

