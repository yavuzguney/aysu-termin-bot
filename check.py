import os, requests
from playwright.sync_api import sync_playwright

START = os.environ["TARGET_URL"]
TOPIC = os.environ["NTFY_TOPIC"]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(START, wait_until="networkidle")
    page.get_by_text("Buchbare Tage anzeigen").click()
    page.wait_for_load_state("networkidle")
    text = page.inner_text("body")
    browser.close()

if "Wunschtage" in text:
    print("Click did not go through, check selector")
elif "keine Termine" in text or "erneut ausführbar" in text:
    print("none")
else:
    requests.post(
        f"https://ntfy.sh/{TOPIC}",
        data="Berlin appointment may be available! Book now.",
        headers={"Title": "LABO slot found", "Priority": "urgent", "Click": START},
    )
    print("AVAILABLE")
