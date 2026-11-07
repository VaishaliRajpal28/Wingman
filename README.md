# Wingman

Wingman is a job application agent I'm building in Python. The goal: it finds jobs, fills in the application forms, and I review and press the final submit button myself.

It isn't limited to tech roles. A kitchen hand job and a data analyst job should both work.

## Status

Early stage. The job-finding part works, and I'm building the rest one small step at a time.

**Working now**
- Search for jobs from a free-text prompt (using Tavily)
- Filter results so only individual job postings are kept, not listing pages
- Extract the content of each posting

**Next**
- Save results to a JSON file
- Study a real Greenhouse application form before automating it
- Fill in applications (stopping before submit so I can review)
- Add an LLM for tailoring and decision-making
- A simple UI

## Why it works this way

Search results usually return listing pages ("100 data jobs in Melbourne"), not the individual job postings. An agent can only apply to a specific job, so Wingman filters the results down to single postings first.

I'm deliberately building the job-fetching part without an LLM first, to understand the problem properly before adding one.

## Running it

Requires Python and [uv](https://docs.astral.sh/uv/).

1. Clone the repo
2. Add your Tavily API key (see the `.env` setup in the code)
3. Run:

```
uv run main.py
```

## Tech

- Python
- [Tavily](https://tavily.com) for search and page extraction
- uv for running the project
