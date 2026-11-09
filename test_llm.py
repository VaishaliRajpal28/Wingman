import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

MODEL = "gpt-5.4-nano-2026-03-17"

response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Reply with the single word: ready"}],
)
print(response.choices[0].message.content)