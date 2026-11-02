import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

url = "https://agl.wd3.myworkdayjobs.com/en-US/AGL_Recruitment/job/Senior-Data-Product---Governance-Analyst_R-0024093"   # copy one with URL ok: True from your output

response = client.extract(urls=[url], extract_depth="advanced")

if response["results"]:
    text = response["results"][0]["raw_content"]
    print("Length:", len(text))
    with open("extract_output.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Saved to extract_output.txt")
else:
    print("FAILED:", response.get("failed_results"))