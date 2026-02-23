# AI Brochure Generator (ChatGPT + Web Scraping)

Generate a short **company brochure** from a website URL using the **ChatGPT API**.

Workflow:
1) Scrape the landing page to collect links  
2) Use ChatGPT to select the **most relevant links** (About, Products, Careers, etc.)  
3) Fetch & clean text from those pages  
4) Ask ChatGPT to generate a **brochure in Markdown**  
5) Render it in a simple web UI and return via API

> ✅ No Jupyter notebooks.  
> ✅ Uses **OpenAI only** (no other frontier model APIs).

---

## Quickstart (Local)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# set OPENAI_API_KEY

uvicorn app.main:app --reload --port 8000
```

Open: http://localhost:8000

---

## Docker

```bash
docker build -t ai-brochure-generator .
docker run --rm -p 8000:8000 --env-file .env ai-brochure-generator
```

---

## API

### POST `/api/brochure`
```json
{
  "company_name": "Hugging Face",
  "website_url": "https://huggingface.co",
  "tone": "professional"
}
```

Returns:
- `brochure_markdown`
- `brochure_html`
- `sources` (pages scraped)

---

## Safety & limits

- Only `http(s)` URLs are accepted.
- Only links on the same domain are followed.
- Max pages is capped (default: 5) to avoid scraping too much.

---

## Project layout
```
app/
  main.py
  config.py
  schemas.py
  services/
    openai_service.py
    brochure_service.py
  utils/
    scraper.py
templates/
  index.html
  result.html
```
