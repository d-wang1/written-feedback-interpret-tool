# written-feedback-interpret-tool
This is a tool that uses LLMs to provide language simplification, tone softening, and case support to aid recipients in a non-real-time text-based feedback processing system.

# Project
The project currently uses React + Vite for the front end (located in `src/`) and FastAPI (Python) for the back end (located in `server/`). The server will auto-update for front-end or back-end changes (as long as python dependencies don't change).

The LLM provider can be easily exchanged in `server/app/main.py` based on need and/or budget. We currently use Groq's free API.

# SETUP: Running the server
1. If you don't currently have Docker or Git installed, install Docker Desktop (https://docs.docker.com/desktop/) and Git
2. Clone the repo: 
   `git clone https://github.com/d-wang1/written-feedback-interpret-tool`
   `cd written-feedback-interpret-tool`
3. Create an `.env` file at the repo root (`written-feedback-interpret-tool/.env`) for your Groq API key. 
   1. To get a free API key, go to https://console.groq.com/home. 
   2. Copy the API key so that your `.env` file has: `GROQ_API_KEY=<your api key>`
   3. _Do NOT upload or share your key. Verify that `.gitignore` does contain `.env` and `.env.*`_
4. Build and run the local server via `docker compose up --build`. 
   1. Visit http://localhost:5173/ on your browser.
   2. Verify server health via http://localhost:8000/api/health


# *(Dev)* TODOs:
- Add repeat-click limit for website to avoid exceeding free quota
  - Disable duplicate requests while loading
- Add configurable model choice
- Add configurable prompt
- Test out prompts w/ Postman

# Common Issues:
1. Quota Exceeded
   Check the LLM dashboard (e.g. https://console.groq.com/dashboard/metrics) for usage details. Wait a few minutes / day to try again. Try not to repeatedly click the submit button.

2. Change in Python dependencies
   If dependencies ever change, rebuild using `docker compose build --no-cache` then `docker compose up`.