# Advance Data Tool

A lead-generation tool that pulls business and job contact details from JustDial, Yelp, and LinkedIn, and exports everything to CSV.

## What it does

You pick a platform, type in a search query (and a city or location depending on the site), and the tool drives a real Chrome browser through the search results, opening each listing and pulling out whatever contact info it can find.

- **JustDial** — searches by city and query, walks through result pages, grabs business name, phone number (including numbers hidden behind a "Call Now" click), and then opens each listing's detail page to look for a website and an email address.
- **Yelp** — searches by query and location, collects business listing links from the results page, and visits each one for the name, phone, email (if listed in the page text), and website link.
- **LinkedIn** — actually scrapes job postings rather than business listings: it searches LinkedIn Jobs for a keyword, opens each job, and captures the job title, company name, and any email or phone number mentioned in the job description.

Since JustDial and Yelp usually require a logged-in session to show full details, the app opens a visible browser window and gives you a configurable pause (default 45 seconds) to log in manually before scraping starts. Your session is then kept in a local Chrome profile folder per site (`profiles/justdial`, `profiles/yelp`, `profiles/linkedin`) so you don't have to log in every run.

All of this runs behind a small Flask web UI — you fill out a form (site, query, city/location, number of pages, headless on/off), hit "Start Extraction," and get a results table plus a CSV file you can download.

## Tech stack

- **Flask** — web UI and routing
- **Selenium** (Chrome via Selenium Manager) — browser automation for all three scrapers
- **pandas** — normalizing scraped rows and writing CSV output
- **python-dotenv** — configuration (default city/location, wait times, etc.) via `.env`

There's no headless-only or API-based scraping here — everything goes through a real Chrome instance, which is why login sessions and "gentle scroll" pauses are built in.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000` in your browser. Chrome needs to be installed locally since Selenium Manager will download a matching driver automatically.

Optional `.env` values: `DEFAULT_CITY`, `DEFAULT_LOCATION`, `DEFAULT_LOGIN_WAIT`, `IMPLICIT_WAIT`, `EXPLICIT_WAIT`, `CSV_PREFIX`.

## Output

Each run writes a timestamped CSV to `exports/` with the columns `name, email, phone, website, source_url`. The results page shows a preview of up to 200 rows, but the full dataset is in the downloaded file.

## A note on usage

JustDial, Yelp, and LinkedIn all have terms of service that restrict automated scraping, and their markup changes often enough that the selectors here may need updates over time. This is meant for personal or internal lead-gen use — keep request volume reasonable and don't rely on it for anything beyond that.

---

**Ankit Singh**
[LinkedIn](https://www.linkedin.com/in/ankit-singh-117925249/)
