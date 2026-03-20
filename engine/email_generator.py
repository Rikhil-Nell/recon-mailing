"""Email sequence generator using OpenAI."""

import json
from pathlib import Path

from openai import OpenAI

from engine.models import CompanyIntel, Contact, Email, EmailSequence
from engine.prompts import (
    COLD_OPEN_PROMPT,
    FOLLOW_UP_PROMPT,
    VALUE_DROP_PROMPT,
    EVENT_CONTEXT,
    CATEGORY_HOOKS,
)


CACHE_DIR = Path("cache/emails")


def _format_company_intel(intel: CompanyIntel, category: str) -> str:
    """Format company intel for injection into prompts."""
    category_hook = CATEGORY_HOOKS.get(category, "")
    return f"""What they do: {intel.summary}
Security relevance: {intel.security_relevance}
Campus/developer programs: {intel.campus_programs}
Recent activity: {intel.recent_news}
Suggested angle: {intel.suggested_angle}
Category-specific insight: {category_hook}"""


def _parse_email_response(response_text: str) -> tuple[str, str]:
    """Parse SUBJECT and BODY from response."""
    subject = ""
    body_lines = []
    in_body = False

    for line in response_text.split("\n"):
        if line.strip().startswith("SUBJECT:"):
            subject = line.strip()[len("SUBJECT:"):].strip()
        elif line.strip() == "BODY:":
            in_body = True
        elif in_body:
            body_lines.append(line)

    body = "\n".join(body_lines).strip()

    # Fallback if parsing fails
    if not subject and not body:
        lines = response_text.strip().split("\n")
        if lines:
            subject = lines[0]
            body = "\n".join(lines[1:]).strip()

    return subject, body


def _get_cache_key(company_name: str, contact_email: str) -> str:
    safe_company = "".join(c if c.isalnum() or c in " _-" else "_" for c in company_name)
    safe_email = "".join(c if c.isalnum() or c in "_-@." else "_" for c in contact_email)
    return f"{safe_company}__{safe_email}"


def get_cached_sequence(company_name: str, contact_email: str) -> EmailSequence | None:
    """Check for cached email sequence."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / f"{_get_cache_key(company_name, contact_email)}.json"
    if cache_path.exists():
        try:
            data = json.loads(cache_path.read_text(encoding="utf-8"))
            emails = [Email(**e) for e in data["emails"]]
            return EmailSequence(
                company_name=data["company_name"],
                contact_name=data["contact_name"],
                contact_email=data["contact_email"],
                emails=emails,
            )
        except Exception:
            return None
    return None


def save_sequence_cache(seq: EmailSequence) -> None:
    """Cache generated email sequence."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / f"{_get_cache_key(seq.company_name, seq.contact_email)}.json"
    data = {
        "company_name": seq.company_name,
        "contact_name": seq.contact_name,
        "contact_email": seq.contact_email,
        "emails": [{"subject": e.subject, "body": e.body, "stage": e.stage} for e in seq.emails],
    }
    cache_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def generate_email_sequence(
    intel: CompanyIntel,
    contact: Contact,
    openai_api_key: str,
    force_refresh: bool = False,
) -> EmailSequence:
    """
    Generate a 3-email sequence for a specific contact at a researched company.
    """
    # Check cache
    if not force_refresh:
        cached = get_cached_sequence(intel.company_name, contact.email)
        if cached:
            return cached

    client = OpenAI(api_key=openai_api_key)
    intel_text = _format_company_intel(intel, contact.category)
    contact_name = contact.name if contact.name else "Team"

    emails = []

    # ── Email 1: Cold Open ────────────────────────────────────────────────
    cold_prompt = COLD_OPEN_PROMPT.format(
        event_context=EVENT_CONTEXT,
        company_name=intel.company_name,
        category=contact.category,
        contact_name=contact_name,
        company_intel=intel_text,
    )

    cold_resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": cold_prompt}],
        temperature=0.7,
        max_tokens=500,
    )

    cold_subject, cold_body = _parse_email_response(cold_resp.choices[0].message.content or "")
    emails.append(Email(subject=cold_subject, body=cold_body, stage="cold_open"))

    # ── Email 2: Follow-up ────────────────────────────────────────────────
    followup_prompt = FOLLOW_UP_PROMPT.format(
        event_context=EVENT_CONTEXT,
        company_name=intel.company_name,
        category=contact.category,
        contact_name=contact_name,
        company_intel=intel_text,
        original_subject=cold_subject,
    )

    followup_resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": followup_prompt}],
        temperature=0.7,
        max_tokens=300,
    )

    followup_subject, followup_body = _parse_email_response(followup_resp.choices[0].message.content or "")
    emails.append(Email(subject=followup_subject, body=followup_body, stage="follow_up"))

    # ── Email 3: Value Drop ───────────────────────────────────────────────
    value_prompt = VALUE_DROP_PROMPT.format(
        event_context=EVENT_CONTEXT,
        company_name=intel.company_name,
        category=contact.category,
        contact_name=contact_name,
        company_intel=intel_text,
    )

    value_resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": value_prompt}],
        temperature=0.7,
        max_tokens=800,
    )

    value_subject, value_body = _parse_email_response(value_resp.choices[0].message.content or "")
    emails.append(Email(subject=value_subject, body=value_body, stage="value_drop"))

    sequence = EmailSequence(
        company_name=intel.company_name,
        contact_name=contact_name,
        contact_email=contact.email,
        emails=emails,
    )

    # Cache the result
    save_sequence_cache(sequence)

    return sequence
