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
            error_msg = str(e)
            
            # Provide more helpful error messages
            if "403" in error_msg:
                user_msg = "Website blocked automated requests (403 Forbidden). It may require manual access or IP whitelisting."
            elif "SSL" in error_msg or "certificate" in error_msg.lower():
                user_msg = "SSL/Certificate error: Website has security issues or blocked the request."
            elif "timeout" in error_msg.lower():
                user_msg = "Website took too long to respond (timeout). Server may be slow or blocking requests."
            elif "connection" in error_msg.lower():
                user_msg = "Connection error: Cannot reach the website. Check if URL is correct or if website is down."
            else:
                user_msg = f"Could not access the website: {error_msg}"
            
            save_page(url, None, "ERROR", error_msg)
            flash(user_msg, "error")
            logging.error(f"{url} → ERROR | {error_msg}")

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
        error_msg = str(e)
        
        # Provide more helpful error messages
        if "403" in error_msg:
            user_msg = "Website blocked automated requests (403 Forbidden). It may require manual access or IP whitelisting."
        elif "SSL" in error_msg or "certificate" in error_msg.lower():
            user_msg = "SSL/Certificate error: Website has security issues or blocked the request."
        elif "timeout" in error_msg.lower():
            user_msg = "Website took too long to respond (timeout). Server may be slow or blocking requests."
        elif "connection" in error_msg.lower():
            user_msg = "Connection error: Cannot reach the website. Check if URL is correct or if website is down."
        else:
            user_msg = f"Could not access the website: {error_msg}"
        
        save_page(url, None, "ERROR", error_msg)
        flash(user_msg, "error")
        logging.error(f"Recheck failed for {url} → {error_msg}")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
