from flask import Flask, render_template, request, send_file, redirect, url_for
import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

from scraper.linkedin import LinkedInStrategy
from scraper.justdial import JustDialStrategy
from scraper.yelp import YelpStrategy

load_dotenv()

app = Flask(__name__)
os.makedirs("exports", exist_ok=True)
os.makedirs("profiles/linkedin", exist_ok=True)
os.makedirs("profiles/justdial", exist_ok=True)
os.makedirs("profiles/yelp", exist_ok=True)

SITE_MAP = {
    "linkedin": LinkedInStrategy,
    "justdial": JustDialStrategy,
    "yelp": YelpStrategy,
}

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/scrape", methods=["POST"])
def scrape():
    site = request.form.get("site", "justdial")
    query = request.form.get("query", "").strip()
    city = request.form.get("city", os.getenv("DEFAULT_CITY", "Mumbai")).strip()
    location = request.form.get("location", os.getenv("DEFAULT_LOCATION", "Mumbai")).strip()
    pages = int(request.form.get("pages", "1"))
    headless = request.form.get("headless") == "on"
    login_wait = int(request.form.get("login_wait", os.getenv("DEFAULT_LOGIN_WAIT", "45")))

    if not query:
        return redirect(url_for("index"))

    Strategy = SITE_MAP.get(site)
    if Strategy is None:
        return redirect(url_for("index"))

    strat = Strategy(
        headless=headless,
        login_wait=login_wait,
        city=city,
        location=location,
        pages=pages,
    )

    try:
        rows = strat.run(query=query)
    finally:
        strat.teardown()

    # Normalize to required columns
    df = pd.DataFrame(rows)
    for col in ["name", "email", "phone", "website", "source_url"]:
        if col not in df.columns:
            df[col] = "NA"
    df = df[["name", "email", "phone", "website", "source_url"]].fillna("NA")

    # Save CSV
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_name = f"{os.getenv('CSV_PREFIX', 'leads_')}{site}_{stamp}.csv"
    csv_path = os.path.join("exports", csv_name)
    df.to_csv(csv_path, index=False)

    # Show top 200 in UI (to keep page light), but file has all
    preview = df.head(200)

    return render_template("results.html",
                           site=site,
                           query=query,
                           city=city,
                           location=location,
                           pages=pages,
                           table=preview.to_dict(orient="records"),
                           csv_name=csv_name)

@app.route("/download/<csv_name>", methods=["GET"])
def download(csv_name):
    path = os.path.join("exports", csv_name)
    if not os.path.exists(path):
        return redirect(url_for("index"))
    return send_file(path, as_attachment=True, download_name=csv_name)

if __name__ == "__main__":
    app.run(debug=True)
