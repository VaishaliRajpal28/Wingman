import json
import re
from playwright.sync_api import sync_playwright

DEBUG = False

# 1. Read the profile file into a Python dictionary
with open("profile.json", encoding="utf-8") as f:
    profile = json.load(f)

url = "https://www.databricks.com/company/careers/education--training/customer-enablement-architect-capability-engineering--ai-adoption-8792853002"

SCAN_JS = """() => {
    return [...document.querySelectorAll('input, select, textarea')].map(el => ({
        tag: el.tagName,
        type: el.type,
        id: el.id,
        label: el.labels && el.labels[0] ? el.labels[0].innerText.trim() : '',
        required: el.required,
        visible: el.offsetParent !== null,
        question: el.closest('fieldset') && el.closest('fieldset').querySelector('legend')
            ? el.closest('fieldset').querySelector('legend').innerText.trim()
            : ''
    }));
}"""

def group_fields(fields):
    """Turn the flat list of inputs into one entry per question."""
    questions = []
    groups = {}  # question text -> its entry, so later options join the same entry

    for f in fields:
        if f["type"] in ("checkbox", "radio") and f["question"]:
            q = f["question"]
            if q not in groups:
                groups[q] = {"question": q, "type": f["type"] + "_group", "options": []}
                questions.append(groups[q])
            groups[q]["options"].append({"label": f["label"], "id": f["id"]})
        else:
            questions.append({"question": f["label"], "type": f["type"], "id": f["id"]})
    return questions


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url)
    page.wait_for_timeout(15000)
    #print("TITLE:", page.title())
    #print("URL:", page.url)
    page.screenshot(path="page.png", full_page=True)
    
    all_fields = []
    for fr in page.frames:
        try:
            found = fr.evaluate(SCAN_JS)
        except Exception:
            continue
        visible = [f for f in found if f["visible"]]
        print(f"FRAME: {fr.url[:80]} -> {len(found)} fields, {len(visible)} visible")
        all_fields.extend(visible)
    
    all_fields = [f for f in all_fields if f["label"] or f["id"]]
    
    if DEBUG:
        with open("form_fields.json", "w", encoding="utf-8") as out:
            json.dump(all_fields, out, indent=2)
    with open("form_fields.json", "w", encoding="utf-8") as out:
        json.dump(all_fields, out, indent=2)
        
        grouped = group_fields(all_fields)
        
    with open("form_questions.json", "w", encoding="utf-8") as out:
        json.dump(grouped, out, indent=2, ensure_ascii=False)
    print(f"{len(all_fields)} fields grouped into {len(grouped)} questions")

    browser.close()