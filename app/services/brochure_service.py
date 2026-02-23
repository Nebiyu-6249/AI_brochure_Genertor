from __future__ import annotations

from typing import List, Tuple
from urllib.parse import urlparse

from app.config import settings
from app.services.openai_service import OpenAIService
from app.utils.scraper import fetch_html, extract_links, fetch_page_text, same_domain


LINK_SELECTOR_SYSTEM = """You are given a list of URLs found on a company website.

Return a JSON object with:
{
  "links": [
    {"type": "about|products|pricing|careers|contact|blog|other", "url": "https://..."}
  ]
}

Rules:
- Prefer pages useful for a brochure: About, Product/Services, Pricing, Customers/Case Studies, Careers, Contact.
- Do NOT include privacy policy, terms, legal, cookie policy, login, sign up, or random tracking URLs.
- Only include URLs on the SAME DOMAIN as the provided website.
- Choose at most 5 links.
- Output MUST be valid JSON only.
"""


BROCHURE_SYSTEM = """You are an assistant that writes concise company brochures.

You will receive the company name, desired tone, and the cleaned text from the website landing page plus a few relevant sub-pages.

Write a brochure in Markdown (no code fences) with these sections:
- Headline (1 line)
- About
- What we do (offerings / products)
- Who it's for (customers / use cases) if known
- Why choose us (differentiators)
- Culture & Careers (only if present)
- Contact / Next steps (CTA)

Rules:
- Keep it ~400-900 words.
- Do NOT invent facts. If unclear, say "Not stated on the site".
- Keep formatting clean and readable.
"""


def validate_http_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http(s) URLs are supported.")


def select_relevant_links(base_url: str, all_links: List[str], client: OpenAIService) -> List[str]:
    # Trim links list to keep prompt bounded
    links_text = "\n".join(f"- {u}" for u in all_links[:200])

    user_prompt = f"""Website: {base_url}

Here are links found on the site:
{links_text}
"""

    data = client.chat_json(LINK_SELECTOR_SYSTEM, user_prompt)
    raw = data.get("links", []) if isinstance(data, dict) else []
    urls = []
    for item in raw:
        u = item.get("url") if isinstance(item, dict) else None
        if not u:
            continue
        if same_domain(base_url, u):
            urls.append(u)

    # Deduplicate + cap
    out = []
    seen = set()
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out[: settings.max_pages]


def build_source_bundle(company_name: str, website_url: str, client: OpenAIService) -> Tuple[str, List[str]]:
    validate_http_url(website_url)
    landing_html = fetch_html(website_url)
    all_links = extract_links(website_url, landing_html)

    relevant = select_relevant_links(website_url, all_links, client)

    sources = [website_url] + relevant
    parts = []
    parts.append(f"# Company: {company_name}\n")
    parts.append(f"## Landing page: {website_url}\n")
    parts.append(fetch_page_text(website_url, max_chars=settings.max_chars_per_page))

    for u in relevant:
        parts.append(f"\n\n## Page: {u}\n")
        parts.append(fetch_page_text(u, max_chars=settings.max_chars_per_page))

    return "\n".join(parts), sources


def generate_brochure(company_name: str, website_url: str, tone: str = "professional") -> Tuple[str, List[str]]:
    client = OpenAIService()
    source_bundle, sources = build_source_bundle(company_name, website_url, client)

    user_prompt = f"""Company name: {company_name}
Desired tone: {tone}

Website content:
{source_bundle}
"""

    brochure_md = client.chat_markdown(BROCHURE_SYSTEM, user_prompt)
    return brochure_md.strip(), sources
