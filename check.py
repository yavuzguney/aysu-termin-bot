import os, re, requests
from playwright.sync_api import sync_playwright

START = os.environ["TARGET_URL"]
TOPIC = os.environ["NTFY_TOPIC"]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    try:
        page.goto(START, wait_until="networkidle")

        # location checkbox is normally ticked already; try, but don't fail
        try:
            page.get_by_role("checkbox", name=re.compile("Abholung fertiger Dokumente")).check(timeout=5000)
        except Exception:
            print("checkbox step skipped")

        page.get_by_text("An diesem Standort einen Termin buchen").first.click(timeout=15000)
        page.wait_for_load_state("networkidle")

        page.get_by_text("Buchbare Tage anzeigen").click(timeout=15000)
        page.wait_for_load_state("networkidle")

        text = page.inner_text("body")
    except Exception as e:
        print("STEP FAILED:", e)
        print("PAGE TEXT AT FAILURE:")
        print(page.inner_text("body")[:1500])
        raise
    finally:
        browser.close()

if "Wunschtage" in text:
    print("Click did not go through, check selector")
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
