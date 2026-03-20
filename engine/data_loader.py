"""Load and clean sponsor contact data from CSV files."""

import csv
import re
from pathlib import Path

from engine.models import Contact, CompanyRecord


# Known company name normalizations
COMPANY_ALIASES = {
    "cap gemini": "Capgemini",
    "capgemini": "Capgemini",
    "zerodha": "Zerodha",
    "zoho": "Zoho",
    "dell": "Dell",
    "microsoft": "Microsoft",
    "redbull": "Red Bull",
    "red bull": "Red Bull",
    "wipro": "Wipro",
    "infosys": "Infosys",
    "cognizant": "Cognizant",
    "jetbrains": "JetBrains",
    "tata motors": "Tata Motors",
    "pwc": "PwC",
    "tcs": "TCS",
    "tech mahindra": "Tech Mahindra",
    "barclays": "Barclays",
    "morgan stanley": "Morgan Stanley",
    "qualcomm": "Qualcomm",
    "stripe": "Stripe",
    "drogo drone": "Drogo Drones",
    "drogo drones": "Drogo Drones",
    "subko": "Subko Coffee",
    "subko coffee": "Subko Coffee",
    "foss united": "FOSS United",
    "namecheap": "Namecheap",
    "cotopaxi": "Cotopaxi Energy",
    "recykal": "Recykal",
    "yash technologies": "Yash Technologies",
    "yellowai": "Yellow.ai",
    "yellow ai": "Yellow.ai",
    "swiggi": "Swiggy",
    "kellton": "Kellton",
    "kellton tech solutions": "Kellton",
    "urban company": "Urban Company",
    "titan": "Titan",
    "just dial": "Just Dial",
    "justeat": "Just Eat Takeaway",
    "clear trip": "Cleartrip",
    "gen spark": "GenSpark",
    "tech gig": "TechGig",
    "open ai": "OpenAI",
    "hdfc": "HDFC Bank",
    "kotak mahindra": "Kotak Mahindra",
    "amazon": "Amazon",
    "ibm": "IBM",
    "hp": "HP",
    "samsung": "Samsung",
    "meta": "Meta",
    "adobe": "Adobe",
    "nvidia": "NVIDIA",
    "intel": "Intel",
    "dream11": "Dream11",
}


def normalize_company_name(name: str) -> str:
    """Normalize company name to canonical form."""
    stripped = name.strip()
    lower = stripped.lower()
    if lower in COMPANY_ALIASES:
        return COMPANY_ALIASES[lower]
    # Title case if no alias found
    return stripped.title() if stripped == stripped.lower() or stripped == stripped.upper() else stripped


def clean_email(email: str) -> str:
    """Clean email string — remove tabs, whitespace."""
    return email.strip().replace("\t", "").strip()


def load_contacts(data_dir: str | Path = "data") -> dict[str, CompanyRecord]:
    """
    Load contacts from CSV and return a dict of CompanyRecord keyed by canonical company name.
    """
    data_path = Path(data_dir)
    csv_file = data_path / "BD 25.2.csv"

    if not csv_file.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file}")

    companies: dict[str, CompanyRecord] = {}

    with open(csv_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("Name") or "").strip()
            company = (row.get("Company name") or "").strip()
            category = (row.get("Catergory") or row.get("Category") or "").strip()
            email = clean_email(row.get("Mail ID") or "")
            phone = (row.get("Phone number") or "").strip()
            cc_name = (row.get("CC name") or "").strip()

            # Skip empty rows or rows without company
            if not company:
                continue

            # Skip rows where name is literally "cell" (placeholder)
            if name.lower() == "cell":
                name = ""

            # Skip rows without email
            if not email:
                continue

            # Normalize company name
            canonical = normalize_company_name(company)

            # Create contact
            contact = Contact(
                name=name,
                company=canonical,
                category=category,
                email=email,
                phone=phone,
                cc_name=cc_name,
            )

            # Add to company record
            if canonical not in companies:
                companies[canonical] = CompanyRecord(
                    canonical_name=canonical,
                    category=category,
                )

            companies[canonical].contacts.append(contact)

    return companies


def get_categories(companies: dict[str, CompanyRecord]) -> list[str]:
    """Get sorted list of unique categories."""
    cats = set()
    for cr in companies.values():
        if cr.category:
            cats.add(cr.category)
    return sorted(cats)


def get_company_website(company_name: str) -> str:
    """
    Best-effort guess at company website URL.
    For most companies, it's just companyname.com.
    """
    # Special cases
    special = {
        "Red Bull": "redbull.com",
        "FOSS United": "fossunited.org",
        "Subko Coffee": "subko.coffee",
        "Just Eat Takeaway": "justeattakeaway.com",
        "Cotopaxi Energy": "cotopaxienergy.com",
        "Dream11": "dream11.com",
        "HDFC Bank": "hdfcbank.com",
        "Kotak Mahindra": "kotak.com",
        "Goldman Sachs": "goldmansachs.com",
        "Morgan Stanley": "morganstanley.com",
        "JP Morgan": "jpmorgan.com",
        "Tata Motors": "tatamotors.com",
        "TATA Trusts": "tatatrusts.org",
        "Larsen&Turbo": "larsentoubro.com",
        "Heritage Foods": "heritagefoods.in",
        "Adani Wilmar Limited": "adaniwilmar.in",
        "Coding Ninjas": "codingninjas.com",
        "GeeksForGeeks": "geeksforgeeks.org",
        "Yellow.ai": "yellow.ai",
        "GenSpark": "genspark.net",
        "Drogo Drones": "drogodrones.com",
        "Urban Company": "urbancompany.com",
        "Wisoft Solutions": "wisoftsolutions.com",
        "Kellton": "kellton.com",
        "Tech Mahindra": "techmahindra.com",
        "TechGig": "techgig.com",
        "Persistent Systems": "persistent.com",
        "Yash Technologies": "yash.com",
        "GMM Pfaudler": "gmmpfaudler.com",
        "IES Ltd": "iesve.com",
        "Apollyon Dynamics": "apollyondynamics.com",
        "Aurenium Capital": "aureniumcapital.com",
        "Josh Talks": "joshtalks.com",
        "Curly Tales": "curlytales.com",
        "House of X": "houseofx.in",
        "Marketing Anatomy": "themarketinganatomy.com",
        "Story Digital": "storydigital.in",
        "Vonage": "vonage.com",
        "BrowserStack": "browserstack.com",
        "Cleartrip": "cleartrip.com",
        "BigBasket": "bigbasket.com",
        "Just Dial": "justdial.com",
        "Swiggy": "swiggy.in",
        "PureEv": "pureev.in",
        "Pepsi": "pepsico.com",
        "Starbucks": "starbucks.in",
        "TalentSprint": "talentsprint.com",
        "Prepinsta": "prepinsta.com",
        "Freyr Energy": "freyrenergy.com",
        "ReNew": "renew.com",
    }

    if company_name in special:
        return f"https://{special[company_name]}"

    # Default: lowercase, remove spaces, add .com
    slug = re.sub(r"[^a-zA-Z0-9]", "", company_name).lower()
    return f"https://{slug}.com"
