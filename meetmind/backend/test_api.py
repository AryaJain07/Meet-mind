import os
import requests
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GEMINI_API_KEY")
print("API Key found:", key[:10] if key else "NOT FOUND")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
r = requests.get(url)
print("Status:", r.status_code)
print("Response:", r.text[:300])