
# AI Brochure Generator (FastAPI + Web Scraping + OpenAI)

Generate a concise **company brochure** (Markdown + rendered HTML) from a public website URL.  
The app scrapes a company’s landing page, asks an OpenAI chat model to pick the most brochure-relevant links (About / Products / Careers, etc.), fetches and cleans the text, then generates a brochure in Markdown.

## Table of contents

- [What it does](#what-it-does)
- [How it works](#how-it-works)
- [Tech stack](#tech-stack)
- [Quickstart (local)](#quickstart-local)
- [Run with Docker](#run-with-docker)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Web UI](#web-ui)
  - [API](#api)
- [Project layout](#project-layout)
- [Safety notes](#safety-notes)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## What it does

- Takes **company name**, **website URL**, and an optional **tone**
- Scrapes the landing page to discover links
- Uses the model to select up to **5** relevant internal links
- Scrapes and cleans text from the selected pages (capped per page)
- Generates a brochure in **Markdown** (and renders it to HTML for the UI)
- Returns:
  - `brochure_markdown`
  - `brochure_html`
  - `sources` (the pages scraped)

## How it works

1. **Scrape landing page** (`requests` + `BeautifulSoup`) to collect `<a href>` links  
2. **Link selection with OpenAI**  
   - The model is instructed to return **JSON** with up to 5 relevant links
   - Non-brochure pages (privacy policy, terms, login, etc.) are discouraged
   - Only **same-domain** links are kept
3. **Fetch & clean text** from the landing page + selected pages  
   - Removes scripts/styles/images and extracts readable text
   - Truncates to `MAX_CHARS_PER_PAGE` chars per page (default: 2000)
4. **Brochure generation with OpenAI**  
   - Produces ~400–900 words in Markdown with consistent sections
   - Instructed **not to invent facts** (uses “Not stated on the site” when needed)
5. **Present results**
   - UI: renders Markdown to HTML and shows scraped sources
   - API: returns Markdown + HTML + sources as JSON

## Tech stack

- **FastAPI** for web server + JSON API
- **Jinja2** templates for the minimal UI
- **Requests + BeautifulSoup** for scraping and text cleaning
- **OpenAI Python SDK** (`openai>=1,<2`) for link selection + brochure generation
- **Markdown** package to render brochure Markdown to HTML

## Quickstart (local)

### Requirements
- Python **3.11+** recommended

### Install & run

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# edit .env and set OPENAI_API_KEY

uvicorn app.main:app --reload --port 8000
```

Open:
- UI: http://localhost:8000
- Health check: http://localhost:8000/healthz

## Run with Docker

```bash
docker build -t ai-brochure-generator .
docker run --rm -p 8000:8000 --env-file .env ai-brochure-generator
```

## Configuration

Configuration is read from `.env` and/or environment variables.

| Variable | Default | Description |
|---|---:|---|
| `OPENAI_API_KEY` | _(required)_ | OpenAI API key used by the SDK |
| `OPENAI_CHAT_MODEL` | `gpt-4o-mini` | Chat model used for link selection + brochure writing |
| `MAX_PAGES` | `5` | Maximum number of sub-pages to scrape (in addition to the landing page) |
| `MAX_CHARS_PER_PAGE` | `2000` | Truncation limit per scraped page to keep prompts bounded |

Notes:
- The code enforces `http(s)` URLs only.
- Only **same-domain** links are followed.

## Usage

### Web UI

1. Navigate to http://localhost:8000
2. Enter:
   - Company name
   - Website URL (must start with `http://` or `https://`)
   - Tone (professional / friendly / investor / recruiting)
3. Click **Generate brochure**

The results page shows:
- Formatted brochure (HTML)
- Raw brochure Markdown
- Sources scraped

## Project layout

```
app/
  main.py                  # FastAPI app + routes (UI + API)
  config.py                # settings + env handling
  schemas.py               # Pydantic request/response models
  services/
    openai_service.py      # OpenAI SDK wrapper (JSON + Markdown)
    brochure_service.py    # scraping + link selection + brochure generation pipeline
  utils/
    scraper.py             # requests + BeautifulSoup helpers
templates/
  index.html               # Tailwind UI form
  result.html              # Rendered brochure + sources
```

## Safety notes

This project includes a very lightweight scraper. Keep these in mind:

- **Respect target sites** (robots.txt, ToS, rate limits). Some sites will block scraping.
- The app restricts to **http(s)** URLs and **same-domain** links, but it is **not** a full SSRF defense.
  - If you expose this publicly, consider adding stronger protections (domain allowlist, IP range blocking, DNS rebinding defenses, request throttling, etc.).
- The number of scraped pages and per-page text is capped to limit prompt size.

## Troubleshooting

- **`OPENAI_API_KEY is not set`**
  - Create `.env` from `.env.example` and set `OPENAI_API_KEY`, or export it in your shell.

- **OpenAI import / SDK errors**
  - Ensure dependencies are installed: `pip install -r requirements.txt`
  - This project targets the **OpenAI Python SDK v1** (`openai>=1,<2`).

- **Scraping failures (403/429/timeouts)**
  - The target site may block automated requests.
  - Try a different URL (sometimes a more specific page works), or increase timeout in `fetch_html()` (code change).

