import logging
from datetime import datetime
import pytz
from flask import Flask, render_template, request, redirect, url_for, flash
from detector import get_page_hash
from database import (
    init_db,
    get_page,
    save_page,
    get_all_pages
)
from requests.exceptions import RequestException

app = Flask(__name__)
app.secret_key = "dev-secret-key"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# Initialize database at startup
init_db()

def utc_to_ist(utc_time_str):
    if not utc_time_str:
        return "-"

    utc = pytz.utc
    ist = pytz.timezone("Asia/Kolkata")

    utc_dt = datetime.fromisoformat(utc_time_str)
    utc_dt = utc.localize(utc_dt)

    ist_dt = utc_dt.astimezone(ist)
    return ist_dt.strftime("%H:%M:%S")



@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"].strip()

        try:
            new_hash = get_page_hash(url)
            old_hash = get_page(url)

            if old_hash is None:
                status = "OK"
            elif new_hash != old_hash:
                status = "CHANGED"
            else:
                status = "OK"

            save_page(url, new_hash, status)
            flash(f"Website checked: {status}", "success")
            logging.info(f"{url} → {status}")

        except Exception as e:
            save_page(url, None, "ERROR", str(e))
            flash(
                "Could not access the website. It may block automated requests.",
                "error"
            )
            logging.error(f"{url} → ERROR | {e}")

        return redirect(url_for("index"))


    raw_pages = get_all_pages()
    pages = []

    for url, status, last_checked, last_changed, last_error in raw_pages:
        pages.append((
            url,
            status,
            utc_to_ist(last_checked),
            utc_to_ist(last_changed),
            last_error
        ))
    return render_template("index.html", pages=pages)

@app.route("/check", methods=["POST"])
def check_url():
    url = request.form["url"].strip()

    try:
        new_hash = get_page_hash(url)
        old_hash = get_page(url)

        if old_hash is None:
            status = "OK"
        elif new_hash != old_hash:
            status = "CHANGED"
        else:
            status = "OK"

        save_page(url, new_hash, status)
        flash(f"Website checked: {status}", "success")
        logging.info(f"Rechecked {url} → {status}")

    except Exception as e:
        save_page(url, None, "ERROR", str(e))
        flash(
            "Could not access the website. It may block automated requests.",
            "error"
        )
        logging.error(f"Recheck failed for {url} → {e}")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
