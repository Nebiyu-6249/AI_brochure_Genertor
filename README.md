# ai-brochure-generator

**Point it at a company's website. It scrapes the landing page, picks the pages worth reading, and generates a clean company brochure in Markdown. FastAPI web UI, JSON API, Docker-ready.**

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?logo=openai&logoColor=white)

## The problem

Sales, recruiting, and investor teams keep asking for one-pagers on companies. Writing one by hand takes 30 to 60 minutes of reading a website that's usually 80% marketing filler. This tool does the reading, picks the pages worth pulling from, and produces a 400 to 900 word brochure that reads like a human wrote it: sourced, no invented facts, consistent structure.

## Flow

```
URL  ──▶  Scrape landing page  ──▶  LLM picks up to 5 relevant links
                                              │
                                              ▼
                        Scrape + clean each page (capped at 2k chars)
                                              │
                                              ▼
                           LLM generates brochure Markdown
                                              │
                                              ▼
                     Rendered HTML preview + Markdown + sources
```

## Design choices worth flagging

- **Two-stage LLM pipeline.** First call chooses which pages to read (returns JSON), second call writes the brochure. Splitting the reasoning is cheaper than doing both in one shot and gives a clean audit trail: you can see which sources went in.
- **Same-domain link filtering.** Only internal links to the same domain are followed. Cheap SSRF defence and keeps the brochure focused on the target company.
- **Per-page character cap.** Each scraped page is truncated to 2000 characters. Keeps token cost predictable regardless of the source site's verbosity.
- **"Don't invent facts" prompt discipline.** The generation prompt explicitly falls back to "Not stated on the site" instead of hallucinating a fact. If it's not on the site, it's not in the brochure.

## Run it

```bash
git clone https://github.com/Nebiyu-6249/ai-brochure-generator.git
cd ai-brochure-generator
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env  # set OPENAI_API_KEY

uvicorn app.main:app --reload --port 8000
```

Or with Docker:

```bash
docker build -t ai-brochure-generator .
docker run --rm -p 8000:8000 --env-file .env ai-brochure-generator
```

Web UI at http://localhost:8000.

## API

```bash
curl -X POST http://localhost:8000/api/brochure \
  -H "Content-Type: application/json" \
  -d '{"company_name":"Acme","website_url":"https://acme.com","tone":"professional"}'
```

Response:

```json
{
  "brochure_markdown": "...",
  "brochure_html": "...",
  "sources": ["https://acme.com/about", "..."]
}
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | required | OpenAI API key |
| `OPENAI_CHAT_MODEL` | `gpt-4o-mini` | Chat model for both link-picking and generation |
| `MAX_PAGES` | `5` | Sub-pages to scrape beyond the landing page |
| `MAX_CHARS_PER_PAGE` | `2000` | Per-page truncation cap |

## Known limits

- Not a defence-grade SSRF prevention layer. Same-domain filtering catches the obvious cases; production use behind auth needs stronger controls (domain allowlists, IP range blocking, DNS rebinding defences).
- Respects nothing about robots.txt. Adding a check is a couple of lines but not shipped yet.
- Client-side JS content is invisible: requests + BeautifulSoup can't execute JavaScript. Modern SPAs that render everything client-side produce a thin brochure.
- No caching. The same URL runs the whole pipeline every time.

## What I'd build next

- Playwright-based scraper as a fallback for JS-rendered sites
- Redis cache keyed by URL with TTL so repeat requests skip the LLM
- Structured output extraction (funding, headcount, tech stack) as a separate JSON alongside the brochure
- Compare-mode: two URLs in, side-by-side brochure out

## Why this exists

A repeatable pattern for "read this site and give me the important parts". The same architecture (LLM-driven link selection, capped ingestion, no-invention prompt) generalises to any structured-extract-from-website workflow, which is a request I keep seeing in real work.

## Author

Nebiyu Gemedu, AI developer in the UAE. [Profile](https://github.com/Nebiyu-6249) · [LinkedIn](https://linkedin.com/in/YOUR-HANDLE) · [Portfolio](https://YOUR-PORTFOLIO)
