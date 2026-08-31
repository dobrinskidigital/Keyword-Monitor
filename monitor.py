#!/usr/bin/env python3
"""Regulation monitor — watches the Federal Register and emails new matches."""

import json
import os
import smtplib
import urllib.parse
import urllib.request
from datetime import date, timedelta
from email.message import EmailMessage

# ============================================================
# CONFIG — this is the only block you edit to reuse for a new client.
# ============================================================

# Federal Register agency slug(s) to watch. Add more to widen coverage,
# e.g. "food-and-drug-administration".
AGENCIES = ["nuclear-regulatory-commission"]

# A document is flagged if it mentions ANY of these words/phrases.
KEYWORDS = [
    "nuclear medicine",
    "byproduct material",
    "radiopharmaceutical",
    "medical use",
    "radiation safety",
]

# Who receives the alert email.
RECIPIENT = "krista@example.com"

# "instant" -> email each new match as it's found (use the 30-min schedule).
# "daily"   -> one digest email per run          (use the once-a-day schedule).
MODE = "instant"

# How many days back to scan each run (safety net for any missed runs).
LOOKBACK_DAYS = 2

# ============================================================
# You shouldn't need to touch anything below here.
# ============================================================

API = "https://www.federalregister.gov/api/v1/documents.json"
STATE_FILE = "state.json"
FIELDS = ["document_number", "title", "abstract", "publication_date",
          "type", "html_url", "agencies"]


def fetch_matches():
    since = (date.today() - timedelta(days=LOOKBACK_DAYS)).isoformat()
    found = {}
    for agency in AGENCIES:
        for term in KEYWORDS:
            params = [
                ("conditions[agencies][]", agency),
                ("conditions[term]", term),
                ("conditions[publication_date][gte]", since),
                ("order", "newest"),
                ("per_page", "50"),
            ]
            params += [("fields[]", f) for f in FIELDS]
            url = API + "?" + urllib.parse.urlencode(params)
            try:
                with urllib.request.urlopen(url, timeout=30) as r:
                    data = json.load(r)
            except Exception as e:
                print(f"Request failed for '{term}': {e}")
                continue
            for doc in data.get("results", []):
                num = doc.get("document_number")
                if num:
                    doc["_matched_keyword"] = term
                    found[num] = doc
    return found


def load_seen():
    try:
        with open(STATE_FILE) as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_seen(seen):
    with open(STATE_FILE, "w") as f:
        json.dump(sorted(seen), f, indent=2)


def build_body(docs):
    blocks = []
    for d in docs:
        agencies = ", ".join(a.get("name", "") for a in d.get("agencies", []))
        blocks.append(
            f"{d.get('type', 'Document')}: {d.get('title', '(no title)')}\n"
            f"Published: {d.get('publication_date', '?')}  |  {agencies}\n"
            f"Matched keyword: {d.get('_matched_keyword', '')}\n"
            f"{(d.get('abstract') or '').strip()}\n"
            f"Read it: {d.get('html_url', '')}\n"
        )
    return "\n" + ("-" * 60 + "\n").join(blocks)


def send_email(subject, body):
    user = os.environ["SMTP_USER"]
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = RECIPIENT
    msg.set_content(body)
    with smtplib.SMTP(os.environ["SMTP_HOST"],
                      int(os.environ.get("SMTP_PORT", "587"))) as s:
        s.starttls()
        s.login(user, os.environ["SMTP_PASS"])
        s.send_message(msg)


def main():
    seen = load_seen()
    new = {n: d for n, d in fetch_matches().items() if n not in seen}

    if not new:
        print("No new documents.")
        return

    docs = list(new.values())
    print(f"{len(docs)} new document(s).")

    if MODE == "daily":
        send_email(f"[Reg Monitor] {len(docs)} new regulatory item(s)",
                   build_body(docs))
    else:
        for d in docs:
            send_email(f"[Reg Monitor] {d.get('title', 'New document')[:120]}",
                       build_body([d]))

    seen.update(new.keys())
    save_seen(seen)
    print("State updated.")


if __name__ == "__main__":
    main()
