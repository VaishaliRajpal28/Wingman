import json
from playwright.sync_api import sync_playwright

URL = "https://www.databricks.com/company/careers/education--training/customer-enablement-architect-capability-engineering--ai-adoption-8792853002"

with open("plan.json", encoding="utf-8") as f:
    plan = json.load(f)

with open("profile.json", encoding="utf-8") as f:
    profile = json.load(f)

def find_form_frame(page, plan):
    """Return the frame (or the page) that contains the form's fields."""
    ids = [item["id"] for item in plan if item["id"]]
    for fr in page.frames:
        for field_id in ids:
            if fr.locator(f'[id="{field_id}"]').count() > 0:
                return fr
    return page.main_frame


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(URL)
    page.wait_for_timeout(3000)

    # Close the cookie banner if there is one
    try:
        page.get_by_role("button", name="Reject All").click(timeout=2000)
    except Exception:
        pass

    form = find_form_frame(page, plan)
    
    filled = []
    not_handled = []
    
    for item in plan:
        if item["action"] != "fill" or not item["id"]:
            continue
        if item["type"] in ("text", "tel", "email"):
            form.locator(f'[id="{item["id"]}"]').fill(item["value"])
            filled.append(item)
        elif item["type"] == "file" and item["value"] == "@resume":
            form.locator(f'[id="{item["id"]}"]').set_input_files(profile["resume_path"])
            filled.append(item)
        else:
            not_handled.append(item)
            
        needs_you = [i for i in plan if i["action"] == "ask_human"]
    left_blank = [i for i in plan if i["action"] == "skip"]

    print("\n" + "=" * 60)
    print("REVIEW - nothing has been submitted")
    print("=" * 60)
    print(f"\nFilled by Wingman ({len(filled)}):")
    for i in filled:
        print(f"  - {i['question'][:80]}")
    print(f"\nWingman could not fill these yet ({len(not_handled)}):")
    for i in not_handled:
        print(f"  - {i['question'][:80]}")
    print(f"\nFor you to answer ({len(needs_you)}):")
    for i in needs_you:
        print(f"  - {i['question'][:80]}  ({i['reason']})")
    print(f"\nLeft blank on purpose ({len(left_blank)}):")
    for i in left_blank:
        print(f"  - {i['question'][:80]}")
    print()

    input("Check the form in the browser, then press Enter here to close...")
    browser.close()