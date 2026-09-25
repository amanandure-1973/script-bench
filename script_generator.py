import os
import json
import re

from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. Add it to your .env file."
    )

client = genai.Client(api_key=API_KEY)


def calculate_word_limit(target_seconds):
    words_per_minute = 150
    return max(40, int((target_seconds / 60) * words_per_minute))


def clean_json_response(text):
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def generate(niche, topic, target_seconds):
    word_limit = calculate_word_limit(target_seconds)

    prompt = f"""
You are an expert short-form video script writer.

Create a spoken video script using these inputs:

Niche: {niche}
Topic: {topic}
Target runtime: {target_seconds} seconds
Approximate total word limit: {word_limit} words

Create exactly three parts:

1. hook
- The first line of the video.
- Create curiosity, relevance, or a strong reason to continue watching.
- Do not use generic introductions.

2. body
- Explain the main idea clearly.
- Give useful information, an example, steps, or a short story.
- Keep it relevant to the niche.
- Make it natural to speak aloud.

3. cta
- End with a natural call-to-action.
- Make the CTA relevant to the topic.

Important:
- Keep the complete script close to the requested runtime.
- Use simple, natural spoken language.
- Do not invent statistics.
- Return ONLY valid JSON.

Required format:

{{
    "hook": "string",
    "body": "string",
    "cta": "string"
}}
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    cleaned_text = clean_json_response(response.text)

    try:
        script = json.loads(cleaned_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Model returned invalid JSON:\n{response.text}"
        ) from exc

    required_fields = ["hook", "body", "cta"]

    for field in required_fields:
        if field not in script:
            raise ValueError(f"Missing required field: {field}")

        if not isinstance(script[field], str):
            raise ValueError(f"{field} must be a string")

        if not script[field].strip():
            raise ValueError(f"{field} cannot be empty")

    return script

