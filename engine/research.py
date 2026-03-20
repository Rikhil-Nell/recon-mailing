"""Company research module using Jina Reader API + OpenAI."""

import json
import os
from pathlib import Path

import requests
from openai import OpenAI

from engine.models import CompanyIntel
from engine.prompts import RESEARCH_PROMPT
from engine.data_loader import get_company_website


CACHE_DIR = Path("cache/research")


def _get_jina_content(url: str, jina_api_key: str = "") -> str:
    """Use Jina Reader API to scrape a URL into clean text."""
    reader_url = f"https://r.jina.ai/{url}"
    headers = {
        "Accept": "text/plain",
    }
    if jina_api_key:
        headers["Authorization"] = f"Bearer {jina_api_key}"

    try:
        resp = requests.get(reader_url, headers=headers, timeout=30)
        resp.raise_for_status()
        # Truncate to ~8000 chars to stay within context limits
        content = resp.text[:8000]
        return content
    except Exception as e:
        return f"[Failed to scrape: {e}]"


def _parse_research_response(response_text: str) -> dict:
    """Parse the structured research response from OpenAI."""
    fields = {
        "SUMMARY": "summary",
        "SECURITY_RELEVANCE": "security_relevance",
        "CAMPUS_PROGRAMS": "campus_programs",
        "RECENT_NEWS": "recent_news",
        "SUGGESTED_ANGLE": "suggested_angle",
    }

    result = {}
    current_field = None
    current_content = []

    for line in response_text.split("\n"):
        matched = False
        for prefix, key in fields.items():
            if line.strip().startswith(f"{prefix}:"):
                if current_field:
                    result[current_field] = " ".join(current_content).strip()
                current_field = key
                current_content = [line.strip()[len(prefix) + 1:].strip()]
                matched = True
                break
        if not matched and current_field:
            current_content.append(line.strip())

    if current_field:
        result[current_field] = " ".join(current_content).strip()

    return result


def _get_cache_path(company_name: str) -> Path:
    """Get cache file path for a company."""
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in company_name)
    return CACHE_DIR / f"{safe_name}.json"


def get_cached_intel(company_name: str) -> CompanyIntel | None:
    """Check if we have cached research for this company."""
    cache_path = _get_cache_path(company_name)
    if cache_path.exists():
        try:
            data = json.loads(cache_path.read_text(encoding="utf-8"))
            return CompanyIntel(**data)
        except Exception:
            return None
    return None


def save_intel_cache(intel: CompanyIntel) -> None:
    """Save research results to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = _get_cache_path(intel.company_name)
    data = {
        "company_name": intel.company_name,
        "website_url": intel.website_url,
        "summary": intel.summary,
        "security_relevance": intel.security_relevance,
        "campus_programs": intel.campus_programs,
        "recent_news": intel.recent_news,
        "suggested_angle": intel.suggested_angle,
        "raw_content": intel.raw_content[:2000],  # Truncate raw for storage
    }
    cache_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def research_company(
    company_name: str,
    category: str,
    openai_api_key: str,
    jina_api_key: str = "",
    force_refresh: bool = False,
) -> CompanyIntel:
    """
    Research a company using Jina Reader API + OpenAI.
    Returns cached results if available unless force_refresh=True.
    """
    # Check cache first
    if not force_refresh:
        cached = get_cached_intel(company_name)
        if cached:
            return cached

    # Step 1: Get company website URL
    website_url = get_company_website(company_name)

    # Step 2: Scrape with Jina
    raw_content = _get_jina_content(website_url, jina_api_key)

    # Step 3: Analyze with OpenAI
    client = OpenAI(api_key=openai_api_key)

    prompt = RESEARCH_PROMPT.format(
        company_name=company_name,
        category=category,
        content=raw_content,
    )

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1000,
    )

    response_text = response.choices[0].message.content or ""
    parsed = _parse_research_response(response_text)

    intel = CompanyIntel(
        company_name=company_name,
        website_url=website_url,
        summary=parsed.get("summary", "No data available"),
        security_relevance=parsed.get("security_relevance", "No data available"),
        campus_programs=parsed.get("campus_programs", "No data available"),
        recent_news=parsed.get("recent_news", "No data available"),
        suggested_angle=parsed.get("suggested_angle", "No data available"),
        raw_content=raw_content,
    )

    # Cache the result
    save_intel_cache(intel)

    return intel
