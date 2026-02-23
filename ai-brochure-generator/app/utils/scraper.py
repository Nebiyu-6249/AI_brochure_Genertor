from __future__ import annotations

from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
from typing import List, Tuple


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def normalize_url(base_url: str, href: str) -> str:
    return urljoin(base_url, href)


def same_domain(a: str, b: str) -> bool:
    try:
        return urlparse(a).netloc == urlparse(b).netloc
    except Exception:
        return False


def fetch_html(url: str, timeout: int = 20) -> str:
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def extract_links(base_url: str, html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for tag in soup.find_all("a"):
        href = tag.get("href")
        if not href:
            continue
        # Skip mailto, tel, etc.
        if href.startswith("mailto:") or href.startswith("tel:") or href.startswith("#"):
            continue
        full = normalize_url(base_url, href)
        links.append(full)
    # Deduplicate, preserve order
    seen = set()
    out = []
    for u in links:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def clean_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input", "svg", "noscript"]):
            irrelevant.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = soup.get_text(separator="\n", strip=True)
    return text


def fetch_page_text(url: str, max_chars: int = 2000) -> str:
    html = fetch_html(url)
    text = clean_text_from_html(html)
    return text[:max_chars]
