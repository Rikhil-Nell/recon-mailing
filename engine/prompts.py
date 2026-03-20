"""Prompt templates for research and email generation."""

# ── Event Context (baked in from Notion doc) ──────────────────────────────

EVENT_CONTEXT = """
EVENT: Recon 2026
TYPE: National-level, DEFCON-style cybersecurity conference and competition
DATES: April 25–27, 2026 (3 days)
VENUE: VIT-AP University, Amaravati, Andhra Pradesh, India
ORGANIZERS: OSC (Open Source Community) × Null Chapter — VIT-AP's open source and cybersecurity student communities
ADVISORY: Dr. Sibi Chakkaravarty (IIT Madras linked)
FUNDING BASELINE: INR 4,97,000

SCALE:
- 600+ registered participants
- 450+ active attendance expected
- 250+ outstation attendees (from across India)
- 80-person organizing workforce
- 15+ target sponsors/partners

FLAGSHIP COMPETITIONS:
- Overnight CTF (Capture The Flag): Jeopardy-style, 12 hours (18:00–06:00), categories: web, pwn, crypto, forensics, OSINT, misc. 20-30 challenges, teams of 1-4.
- Overnight KOTH (King of the Hill): 8 hours (22:00–06:00), 8-12 target boxes, attack/defend hybrid format.

SIDE EVENTS (10+):
- RFID Lock Hunt (campus-wide clue trail + lockbox challenge)
- Hardware Badge Building + IoT Village (soldering, firmware security)
- Gaming Arena (FIFA/Valorant/CS2 tournaments)
- Web Exploit Dojo (OWASP top 10 guided labs)
- OSINT Corner (investigation puzzles)
- Forensics Sprint (memory dumps, pcap analysis, stego)
- AI Red-Team Mini-Lab (prompt injection, jailbreak defenses)
- Sponsor Demo Street (interactive sponsor challenges)
- Bug Bounty App Quest (hidden CTF easter egg)
- Security Career Clinic (CV triage, GitHub review, mock interviews)

TECHNICAL INFRASTRUCTURE:
- Fully cloud-hosted on AWS (CTFd, KOTH targets, app backend)
- OpenVPN overlay network for competition isolation
- Custom event app with live scoring, queuing, passport points system

AUDIENCE PROFILE:
- CS/IT/ECE engineering students (years 1-4)
- Strong interest in cybersecurity, ethical hacking, CTF competitions
- Mix of beginners and experienced players
- Active on platforms like HackerEarth, Unstop, CTFtime
- Many actively seeking internships and jobs in security/tech

WHAT SPONSORS GET:
- Direct access to a highly niche, technically skilled audience
- Talent pipeline: these students actively compete in CTFs and hack — they are the exact candidates security teams want to hire
- Interactive activation opportunities (not passive logo placement): sponsor challenges, demo slots, career booths, API/product integrations
- Brand positioning among India's next-gen security community
- Measurable engagement: footfall counts, challenge participation, lead scans
- Post-event sponsor report with detailed metrics

SPONSOR TIERS:
- Title Sponsor (1 slot): naming rights, keynote slot, prime stall, flagship challenge, app banner
- Gold Sponsor (up to 4): stage placement, standard stall, demo block, mini challenge
- Community Sponsor (multiple): logo wall, shared kiosk, swag partner
"""

# ── Research Prompt ───────────────────────────────────────────────────────

RESEARCH_PROMPT = """You are a sponsor outreach research assistant for a cybersecurity event called Recon 2026.

Given the following scraped content from a company's website, extract intelligence that would be useful for crafting a sponsorship pitch. Focus on:

1. **What they do**: Core products/services in 2-3 sentences
2. **Security relevance**: Any connection to cybersecurity, developer tools, cloud security, infrastructure security, or adjacent fields. If none directly, note what technical areas they work in.
3. **Campus/Developer programs**: Any university partnerships, developer evangelism, campus hiring, internship programs, hackathon sponsorships, open source involvement
4. **Recent activity**: Any recent product launches, blog posts about community engagement, hiring pushes, or relevant news
5. **Suggested sponsorship angle**: Based on all the above, craft a specific 1-2 sentence hook for why sponsoring a cybersec event makes sense for THIS specific company. Make it concrete, not generic.

Company: {company_name}
Category: {category}

--- SCRAPED CONTENT ---
{content}
--- END CONTENT ---

Respond in this exact format:
SUMMARY: [what they do]
SECURITY_RELEVANCE: [security connection]
CAMPUS_PROGRAMS: [campus/developer programs]
RECENT_NEWS: [recent activity]
SUGGESTED_ANGLE: [specific sponsorship hook]
"""

# ── Email Generation Prompts ──────────────────────────────────────────────

COLD_OPEN_PROMPT = """You are writing a cold sponsorship outreach email for Recon 2026 — a national-level, DEFCON-style cybersecurity event at VIT-AP University.

RULES:
- This email must be 4-6 sentences MAXIMUM. Not one sentence more.
- DO NOT list event features in bullet points. No bullet points at all.
- DO NOT include a full event description. The goal is to get a REPLY, not close the deal.
- Lead with what the SPONSOR gets, not what you're doing.
- Reference something specific about their company to show you've done research.
- Tone: confident, peer-to-peer, not supplicative. You're offering value, not begging.
- End with a single clear ask (usually: "Would it make sense to share our sponsorship brief?")
- Sign off as "Team Recon 2026 | OSC × Null Chapter, VIT-AP University"
- Subject line should be short, specific, and NOT generic like "Sponsorship Opportunity"

{event_context}

COMPANY INTEL:
Company: {company_name}
Category: {category}
Contact name: {contact_name}
{company_intel}

Write the email. Return it in this format:
SUBJECT: [subject line]
BODY:
[email body]
"""

FOLLOW_UP_PROMPT = """You are writing a follow-up email for a sponsorship pitch that got no reply after 5 days. This is for Recon 2026 — a DEFCON-style cybersecurity event at VIT-AP University.

RULES:
- 2-3 sentences MAXIMUM. Ultra brief.
- DO NOT repeat the original pitch.
- Add ONE new hook — either a new data point, a competitor/peer company reference, or a specific activation idea for them.
- Tone: casual, not pushy. Acknowledge they're busy.
- NO bullet points, NO event descriptions.
- End with a low-friction ask.
- Sign off as "Team Recon 2026"

Original cold email subject: {original_subject}

COMPANY INTEL:
Company: {company_name}
Category: {category}
Contact name: {contact_name}
{company_intel}

{event_context}

Write the follow-up. Return it in this format:
SUBJECT: Re: {original_subject}
BODY:
[email body]
"""

VALUE_DROP_PROMPT = """You are writing the detailed value-drop email for a sponsor who has REPLIED with interest to your initial outreach about Recon 2026 — a national-level, DEFCON-style cybersecurity event at VIT-AP University.

This is where you lay out the full value prop. They've already shown interest, so now give them substance.

RULES:
- Structured and detailed but not bloated. Use short paragraphs, not walls of text.
- Open by thanking them for their interest and acknowledging their specific response.
- Lay out 3-4 concrete things they'd get as a sponsor, tailored to their company:
  * What kind of activation/challenge/demo would work for them
  * The audience they'd reach (be specific: "600+ CS/security students, many actively CTF competitors")
  * Brand positioning among India's next-gen security talent
  * Any talent pipeline / hiring angle
- Mention the sponsor tier options briefly (Title / Gold / Community) without going into price details — offer to share the full sponsorship deck.
- End with a clear next step (call, meeting, or "happy to share our full deck").
- Sign off as the team with contact details.

{event_context}

COMPANY INTEL:
Company: {company_name}
Category: {category}
Contact name: {contact_name}
{company_intel}

Write the value-drop email. Return it in this format:
SUBJECT: [subject line]
BODY:
[email body]
"""

# ── Category-Specific Hooks ───────────────────────────────────────────────
# These are injected into company intel to give the AI extra context per category

CATEGORY_HOOKS = {
    "Cybersecurity & Dev Tools": "This company builds tools that our participants literally use. Sponsoring means product visibility with power users who will advocate for their tools in future jobs. Consider: sponsor challenge using their product, developer workshops, swag for top performers.",
    "Cloud & AI": "Cloud and AI companies benefit from showcasing their platforms to the exact students who will choose cloud providers for their startups and future employers. Consider: cloud security quest challenge, AI red-team lab sponsorship, compute credits as prizes.",
    "Fintech & Banking": "Banks and fintech companies have massive security teams and are always hiring. This is a direct talent pipeline event — the students here are the ones who'll ace their security engineering interviews. Consider: secure coding sprint, bug bounty challenge, fast-track interview desk.",
    "IT Services & Consulting": "IT services companies hire in bulk from VIT-AP and similar tier-1/tier-2 campuses. Sponsoring builds brand preference among the exact students they'll be offering packages to. Consider: career clinic sponsorship, resume review desk, campus brand activation.",
    "SaaS & Software": "SaaS companies benefit from developer mindshare. Getting their product in front of 600 technically engaged students creates lasting brand awareness. Consider: API integration challenge, product demo slot, developer swag.",
    "Hardware & Electronics": "Hardware companies can showcase their tech in a hands-on environment. The IoT Village and Hardware Badge events are perfect for product demos. Consider: hardware badge component sponsorship, IoT challenge, equipment showcase.",
    "EdTech & Learning": "EdTech companies can reach students at the exact moment they're most motivated to learn security skills. Direct lead generation opportunity. Consider: workshop sponsorship, course voucher prizes, learning path integration.",
    "Semiconductor": "Semiconductor companies can connect with students interested in hardware security, embedded systems, and chip-level vulnerabilities. Consider: hardware hacking challenge sponsorship, firmware security workshop.",
    "Food & Beverage": "F&B brands get massive visibility during a 3-day event with overnight sessions where participants need energy. 600+ students over 3 days = significant brand exposure. Consider: snack/drink sponsorship for overnight competitions, branded refreshment zones, campus activation.",
    "Gaming": "Gaming companies fit perfectly with the gaming arena side event. Direct audience overlap with competitive gamers who also compete in CTFs. Consider: gaming tournament sponsorship, prize pool contribution, in-game item giveaways.",
    "Automotive & EV": "Automotive companies benefit from campus brand awareness and tech talent recruitment. Consider: EV tech demo, career booth, innovation challenge.",
    "Energy & Sustainability": "Green energy companies can position themselves as forward-thinking sponsors at a tech event. Consider: sustainability-focused side challenge, campus brand activation.",
    "Manufacturing & Engineering": "Engineering companies benefit from access to students with problem-solving and systems thinking skills. Consider: engineering challenge, career booth, hardware demos.",
    "Media & Entertainment": "Media companies can get content and coverage from a high-energy, visually compelling event. Consider: media partnership, content coverage deal, social media amplification.",
    "Talent & HR Tech": "HR tech companies are literally in the business of connecting talent with companies. A cybersec event is a concentrated talent pool. Consider: talent assessment challenge, hiring platform demo, resume clinic partnership.",
    "Social Media & Platforms": "Social platforms benefit from developer engagement and campus brand love. Consider: developer API challenge, content creation challenge, campus ambassador tie-up.",
    "Telecom": "Telecom companies provide the connectivity backbone. Consider: event Wi-Fi/connectivity sponsorship, networking infrastructure.",
}
