import os, requests
from playwright.sync_api import sync_playwright

START = os.environ["TARGET_URL"]
TOPIC = os.environ["NTFY_TOPIC"]
LOCATION = "Fahrerlaubnisbehörde - Abholung fertiger Dokumente"


def is_blocked(t):
    return "Zu viele Anfragen" in t or "Too many requests" in t


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    try:
        page.goto(START, wait_until="networkidle")
        page.wait_for_timeout(1500)  # let the page's scripts attach
        text = page.inner_text("body")

        if is_blocked(text):
            print("blocked by site, no alert")
            raise SystemExit(0)

        # tick the location; the booking button stays disabled until then
        try:
            page.get_by_role("checkbox", name=LOCATION).first.check(timeout=8000)
        except Exception:
            print("checkbox() failed, trying label click")
            page.get_by_text(LOCATION).first.click(timeout=8000)

        page.wait_for_selector("#appointment_submit:not([disabled])", timeout=10000)
        page.click("#appointment_submit")
        page.wait_for_load_state("networkidle")

        page.get_by_text("Buchbare Tage anzeigen").click(timeout=15000)
        page.wait_for_load_state("networkidle")

        text = page.inner_text("body")
    except SystemExit:
        raise
    except Exception as e:
        print("STEP FAILED:", str(e)[:400])
        try:
            print("LABELS ON PAGE:", page.locator("label").all_inner_texts()[:25])
            print("PAGE TEXT AT FAILURE:")
            print(page.inner_text("body")[:800])
        except Exception:
            pass
        raise
    finally:
        browser.close()

if is_blocked(text):
    print("blocked by site, no alert")
elif "Wunschtage" in text:
    print("Click did not go through")
elif "keine Termine" in text or "erneut ausführbar" in text:
    print("none")
else:
    print(text[:500])
    requests.post(
        f"https://ntfy.sh/{TOPIC}",
        data="Berlin appointment may be available! Book now.",
        headers={"Title": "LABO slot found", "Priority": "urgent", "Click": START},
    )
    print("AVAILABLE")
