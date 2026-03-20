"""Data models for the Recon outreach engine."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Contact:
    name: str
    company: str
    category: str
    email: str
    phone: str = ""
    cc_name: str = ""  # Team member assigned


@dataclass
class CompanyIntel:
    company_name: str
    website_url: str
    summary: str  # What the company does
    security_relevance: str  # Why they'd care about a cybersec event
    campus_programs: str  # Any developer relations / campus / hiring programs
    recent_news: str  # Recent launches, initiatives
    suggested_angle: str  # The hook for sponsorship outreach
    raw_content: str = ""  # Raw scraped content (for debugging)


@dataclass
class Email:
    subject: str
    body: str
    stage: str  # "cold_open", "follow_up", "value_drop"


@dataclass
class EmailSequence:
    company_name: str
    contact_name: str
    contact_email: str
    emails: list[Email] = field(default_factory=list)


@dataclass
class CompanyRecord:
    """Aggregated record for a company with all contacts and outreach state."""
    canonical_name: str
    category: str
    contacts: list[Contact] = field(default_factory=list)
    status: str = "not_started"  # not_started, researched, email_1_sent, follow_up_sent, replied, closed, declined
    intel: Optional[CompanyIntel] = None
    email_sequences: dict[str, EmailSequence] = field(default_factory=dict)  # keyed by contact email
