# Wingman

Wingman is a job application assistant I'm building in Python. Give it a job application link, and it reads the form, plans the answers, and fills it in. Then it stops so I can review everything and press the final submit button myself.

It is not meant to be limited to tech roles. The long-term goal is for a kitchen hand job and a data analyst job to both work.

## Status: V1

V1 works on a single application URL, tested so far on Greenhouse forms. It uses a dummy profile for demos.

**Working now**
- Inspect an application form and extract its fields and questions (Playwright)
- Plan the answers: hard-coded safety rules first, then an LLM for the rest
- Fill in text fields and upload a resume
- Print a review report of what was filled, what is left for me, and what was skipped on purpose
- Stop before submit, so the final decision stays with me

**Known gaps**
- Dropdown fields (for example Country and City) are not handled yet
- Only tested on a small number of Greenhouse forms so far

**Next (V2)**
- Handle dropdowns and test on more forms
- A simple UI
- Query-based job discovery: describe the roles you want, and Wingman finds them
- Retrieve details from a resume and tailor application materials for each role

## How it works

```
Application URL
      |
Form inspection        (Playwright reads the fields and questions)
      |
Deterministic          (plain Python: safety rules, no LLM needed)
processing
      |
LLM mapping            (matches remaining questions to the profile)
      |
Application plan       (an answer decided for each field)
      |
Form filling           (Playwright types answers and uploads the resume)
      |
Human review           (I check everything and submit myself)
```

## Design principles

**Not every problem needs an LLM.** Every model call adds latency, cost and a chance of error. Anything predictable stays in plain Python. The LLM is only used where understanding context is needed.

**Safety rules run before the AI.** Sensitive questions are skipped on purpose instead of being left to the model's judgment.

**Automation should not remove the human.** Wingman never submits an application on its own.

## Project structure

- `scan_form.py` inspects the form and writes `form_questions.json`
- `planner.py` applies the safety rules, then the LLM, and writes `plan.json`
- `fill_form.py` fills the form from `plan.json` and prints the review report
- `main.py` job search using Tavily (free-text prompt, filters results down to individual postings)

## Running it

Requires Python and [uv](https://docs.astral.sh/uv/).

1. Clone the repo
2. Add your API keys in a `.env` file (OpenAI for the planner, Tavily for search)
3. Install the Playwright browsers if you haven't already
4. Run the steps in order:

```
uv run scan_form.py
uv run planner.py
uv run fill_form.py
```

The model call lives in one function, so the LLM provider can be swapped easily.

## Tech

- Python
- [Playwright](https://playwright.dev/python/) for reading and filling forms
- OpenAI API for the planner (provider can be swapped)
- [Tavily](https://tavily.com) for job search and page extraction
- [uv](https://docs.astral.sh/uv/) for running the project

## Author

Built by Vaishali. More at [github.com/VaishaliRajpal28](https://github.com/VaishaliRajpal28).
