# Website Change Detector – Improvements & Project Evolution

This document tracks the evolution of the **Website Change Detector** project, outlining feature additions, technical decisions, and improvements made over time.

---

## ✅ V1 – Initial Version (Core Functionality)

### What Was Done

### 1. **Core Change Detection Logic**
- Implemented hash-based website change detection using SHA-256
- Normalized webpage content to avoid false positives from minor formatting differences
- Compared current page hash with previously stored hash to detect content updates
- Designed detection logic to be framework-agnostic and reusable

### 2. **Flask Web Application**
- Built a lightweight Flask application as a thin interface layer
- Implemented routes to:
  - Add new website URLs
  - Manually trigger website checks
  - View tracked website statuses
- Used server-side rendering with Jinja templates for simplicity

### 3. **SQLite Database Persistence**
- Used SQLite as a lightweight embedded database
- Stored:
  - Website URL
  - Content hash
  - Last checked timestamp
  - Last changed timestamp
- Ensured data persistence across application restarts

### 4. **Manual Monitoring Workflow**
- Designed the system around explicit user-triggered checks (“Check now”)
- Avoided background schedulers to keep logic simple and debuggable
- Focused on correctness before automation

### 5. **Clean Project Architecture**
- Separated responsibilities across modules:
  - `detector.py` → core change detection logic
  - `database.py` → database access layer
  - `app.py` → Flask routing and orchestration
- Ensured business logic remained independent of the web framework

---

### Performance

| Operation | Time |
|---|---|
| Page fetch + hashing (requests) | ~1–2 seconds |
| Hash comparison | O(1) |
| Database read/write | < 50 ms |

---

### Files Introduced

- `app.py` – Flask application
- `detector.py` – Hash-based detection logic
- `database.py` – SQLite persistence layer
- `templates/index.html` – Basic user interface
- `requirements.txt` – Initial dependency list
- `README.md` – Project overview and usage

---

### Limitations in V1 (Known & Intentional)
- No handling for bot-blocking or JavaScript-heavy websites
- Limited error visibility for users
- Minimal UI styling
- No fallback mechanism for failed requests

These limitations were **deliberately addressed in V2**.

---

## 🚀 V2 – Reliability, UX & Real-World Website Handling

### What Was Done

### 1. **UI Improvements**
- Increased table width for better horizontal layout
- Reduced padding and font sizes for compact row display
- Fixed inline button styling for per-URL actions
- Removed excessive vertical spacing
- Improved readability without introducing frontend frameworks

### 2. **Bot Detection Bypass – Requests Optimization**
- Updated User-Agent to a realistic Chrome browser string
- Added comprehensive HTTP headers:
  - `Accept`
  - `Accept-Language`
  - `Referer`
  - Security-related headers
- Implemented request delay (0.5s) to simulate human behavior
- Added session management for cookie persistence
- Increased request timeout from 10s to 15s
- Implemented retry logic with SSL verification fallback

### 3. **Selenium Fallback for Blocked Websites ✨**
- Integrated Selenium WebDriver with `webdriver-manager`
- Implemented automatic fallback to Selenium when requests are blocked (e.g., HTTP 403)
- Configured Selenium to run in headless mode
- Successfully handled websites that explicitly block bots:
  - `suit.cibil.com` → Accessible via Selenium (~7–8s)
  - `affidavit.eci.gov.in` → Accessible via Selenium (~7–8s)

### 4. **Improved Error Handling & Messaging**
- Replaced generic failures with meaningful user-facing messages:
  - 403 Forbidden → Website blocks automated requests
  - SSL/Certificate errors → Website has security issues
  - Timeouts → Website took too long to respond
  - Connection errors → Cannot reach the website
- Added structured logging for debugging and observability

### 5. **Updated Dependencies**
- Cleaned `requirements.txt` to include only essential packages:
  - Flask
  - requests
  - pytz
  - selenium
  - webdriver-manager

---

### Performance

| Website Type | Method | Time |
|---|---|---|
| Standard websites | Requests | ~1–2 seconds |
| Bot-blocking websites | Selenium fallback | ~7–8 seconds |
| Google / Wikipedia | Requests | ~1–2 seconds |

---

### How It Works

1. **Primary attempt**: Uses the fast `requests` library
2. **If blocked (403)**: Automatically switches to Selenium (real browser)
3. **If SSL error**: Retries without verification, then Selenium
4. **User experience**: Fully transparent – no manual intervention required

---

### Files Modified in V2

- `detector.py` – Selenium fallback and improved request headers
- `app.py` – Enhanced error handling and user feedback
- `templates/index.html` – UI compactness and usability improvements
- `requirements.txt` – Clean dependency list
- `IMPROVEMENTS.md` – Project evolution documentation

---

### Testing

- Included a detailed test script: `test_detailed.py`
- Verified functionality against:
  - normal websites
  - bot-blocking websites
  - SSL and timeout edge cases
- Confirmed all previously failing websites are now handled successfully

---

## 🔮 Future Enhancements (Planned)

- Scheduled background checks (cron-based)
- Email or notification alerts
- Deployment with persistent storage
- API endpoints for programmatic access

---

This document will continue to evolve as the project grows.