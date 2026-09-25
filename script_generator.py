import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. Add it to your .env file."
    )

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def calculate_word_limit(target_seconds):
    """
    Estimate the number of spoken words based on
    an average speaking speed of about 150 words/minute.
    """
    words_per_minute = 150
    return max(40, int((target_seconds / 60) * words_per_minute))


def clean_json_response(text):
    """Remove Markdown code fences if the model returns them."""
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

The script must contain exactly three parts:

1. hook
- The first line of the video.
- It must immediately create curiosity, relevance, or a strong reason to continue watching.
- Avoid generic introductions such as "Hey guys, welcome back."

2. body
- Explain the main idea clearly.
- Give useful information, an example, steps, or a short story depending on the topic.
- Keep the content relevant to the niche.
- Make it sound natural when spoken aloud.

3. cta
- End with a natural call-to-action.
- The CTA should fit the topic instead of sounding forced.

Important:
- The complete spoken script should be close to the requested runtime.
- Do not add unnecessary explanations.
- Do not invent statistics unless they are clearly presented as examples.
- Use simple, natural spoken language.
- Return ONLY valid JSON.

Required JSON format:

{{
    "hook": "string",
    "body": "string",
    "cta": "string"
}}
"""

    response = model.generate_content(prompt)

    raw_text = response.text
    cleaned_text = clean_json_response(raw_text)

    try:
        script = json.loads(cleaned_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Model returned invalid JSON:\n{raw_text}"
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
