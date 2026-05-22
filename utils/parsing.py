import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d[\s-]?)?(?:\(?\d{3,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4}")

def extract_email(text: str):
    if not text:
        return None
    m = EMAIL_RE.search(text)
    return m.group(0) if m else None

def extract_phone(text: str):
    if not text:
        return None
    m = PHONE_RE.search(text)
    return m.group(0) if m else None

def clean_url(url: str):
    if not url:
        return None
    return url.strip()

def na(val):
    return val if (val and str(val).strip()) else "NA"
