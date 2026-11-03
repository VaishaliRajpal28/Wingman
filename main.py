import os
import re
import sys
import json

# Make sure special characters (e.g. "─" or emojis in job text) print correctly on Windows
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from tavily import TavilyClient

# Load variables from the .env file into the environment
load_dotenv()

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

DEBUG = True                    
# Only searching websites that actually host job postings.
# Without this, Tavily searches the whole web and returns articles like
# "Top 10 software engineering jobs" instead of real postings.
JOB_DOMAINS = [
    "boards.greenhouse.io",
    "job-boards.greenhouse.io",
    "jobs.lever.co",
    "jobs.ashbyhq.com",
    "myworkdayjobs.com",
]

# Only keep URLs that point to ONE specific job.
# Every job board has a different URL shape for a single posting vs. a
# search/category page. e.g.
#   Single posting:  seek.com.au/job/12345678
#   Listing page:    seek.com.au/software-engineer-jobs/in-melbourne

POSTING_URL_PATTERNS = [
    r"seek\.com\.au/job/\d+",
    r"indeed\.com/.*(viewjob|jk=)",
    r"linkedin\.com/jobs/view/\d+",
    r"jora\.com/job/",
    r"glassdoor\.com\.au/job-listing/",
    r"boards\.greenhouse\.io/[^/]+/jobs/\d+",
    r"jobs\.lever\.co/[^/]+/[0-9a-f-]{36}",
    r"jobs\.ashbyhq\.com/[^/]+/[0-9a-f-]{36}",
    r"myworkdayjobs\.com/.*/job/",
]


def is_job_posting_url(url):
    """Return True if the URL matches the pattern of a single job posting."""
    return any(re.search(pattern, url) for pattern in POSTING_URL_PATTERNS)


# Check the page text.
# A real posting usually contains several of these section headings, while a
# listing page is just many short snippets. Useful for catching listing pages
# whose URL accidentally matched a pattern above.

POSTING_KEYWORDS = [
    "responsibilities",
    "requirements",
    "qualifications",
    "about the role",
    "apply now",
    "what you'll do",
    "key skills",
]


def looks_like_posting_text(job):
    """Return True if the page text contains at least 2 typical job-posting phrases."""
    # raw_content is the full page text; fall back to the short snippet if missing
    text = (job.get("raw_content") or job.get("content") or "").lower()
    hits = sum(keyword in text for keyword in POSTING_KEYWORDS)
    return hits >= 2

def get_full_text(url):
    """Open one job page with Tavily extract and return its full text ('' if it fails)."""
    client = TavilyClient(api_key=TAVILY_API_KEY)
    response = client.extract(urls=[url], extract_depth="advanced")
    if response["results"]:
        return response["results"][0]["raw_content"]
    return ""

def search_jobs(query):
    """Search job sites and return only results that look like single postings."""
    client = TavilyClient(api_key=TAVILY_API_KEY)

    response = client.search(
        query,
        max_results=20,                 
        search_depth="basic",        
        include_domains=JOB_DOMAINS,    
        include_raw_content=True
    )

    results = response["results"]
    print(f"Tavily returned {len(results)} results before filtering\n")
    #print(results)

    # STEP 2 + 3: keeping only results that pass both checks
    kept = []
    for job in results:
        url_ok = is_job_posting_url(job["url"])
        text_ok = False

        # Only open pages whose URL looks like a single job (saves time and credits)
        if url_ok:
            job["raw_content"] = get_full_text(job["url"])
            text_ok = looks_like_posting_text(job)

        if DEBUG:
            print(f"URL ok: {url_ok} | text ok: {text_ok} | {job['url']}")

        if url_ok and text_ok:
            kept.append(job)
 
    print()  # blank line after the debug block
    return kept

def save_jobs(jobs, filename="jobs.json"):
    """Save the list of jobs to a JSON file."""
    to_save = [
        {
            "title": job.get("title"),
            "url": job.get("url"),
            "description": job.get("raw_content"),
        }
        for job in jobs
    ]
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(to_save, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(to_save)} jobs to {filename}")

def main():
    query = input("What jobs are you looking for? ")
    jobs = search_jobs(query)

    print(f"\n{'=' * 60}")
    print(" WINGMAN | JOB SEARCH RESULTS")
    print(f"{'=' * 60}")
    print(f"Individual postings found: {len(jobs)}\n")

    for index, job in enumerate(jobs, start=1):
        # .get() with a default avoids crashes if a field is missing
        title = job.get("title", "Title unavailable")
        url = job.get("url", "No URL available")
        description = job.get("content", "No description available")

        print(f"{'─' * 60}")
        print(f"JOB {index}: {title}")
        print(f"{'─' * 60}")
        print(f"Description:\n{description[:400]}...")
        print(f"\nApply / View Job:\n{url}\n")
    save_jobs(jobs)



if __name__ == "__main__":
    main()