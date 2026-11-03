from playwright.sync_api import sync_playwright

url = "https://www.databricks.com/company/careers/education--training/customer-enablement-architect-capability-engineering--ai-adoption-8792853002"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url)
    print("Page title:", page.title())
    page.wait_for_timeout(80000)
    browser.close()