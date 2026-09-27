import json
import os
import re
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

try:
    from google import genai
except ImportError:
    genai = None

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-2.5-flash")

def _extract_json(text: str):
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise

def _fallback_outline(story_prompt, character_name, setting, tone, art_style, panel_count):
    titles = ["The Beginning", "A Strange Discovery", "The Challenge", "The Big Moment",
              "A New Beginning", "The Unexpected Twist", "The Final Challenge", "The Ending"]
    panels = []
    for i in range(panel_count):
        title = titles[i] if i < len(titles) else f"Adventure Part {i + 1}"
        if i == 0:
            scene = f"{character_name} begins an exciting adventure in {setting}. The story starts with the idea: {story_prompt}."
        elif i == panel_count - 1:
            scene = f"{character_name} reaches the conclusion of the adventure in {setting} and learns an important lesson."
        else:
            scene = f"{character_name} continues the adventure in {setting}. A new event connected to '{story_prompt}' creates a {tone.lower()} situation."
        image_prompt = f"{art_style} comic illustration, {character_name}, {setting}, {scene}, expressive characters, cinematic composition, detailed background, vibrant comic artwork"
        panels.append({"panel_number": i + 1, "title": title, "scene_description": scene, "image_prompt": image_prompt})
    return panels

def generate_outline(story_prompt, character_name, setting, tone, art_style, panel_count=5):
    if not GEMINI_API_KEY or genai is None:
        return _fallback_outline(story_prompt, character_name, setting, tone, art_style, panel_count)
    prompt = f"""You are ComicCraft, an AI comic story planner.
Create a {panel_count}-panel comic outline.
Story idea: {story_prompt}
Main character: {character_name}
Setting: {setting}
Story tone: {tone}
Art style: {art_style}
Return ONLY valid JSON as an array. Each item must contain:
{{"panel_number": 1, "title": "Panel title", "scene_description": "Short scene description", "image_prompt": "Detailed visual prompt for an AI image generator"}}
Create exactly {panel_count} panels. Keep the same main character throughout. Make the story flow naturally. Do not use markdown."""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(model=GEMINI_FLASH_MODEL, contents=prompt)
        data = _extract_json(response.text)
        if not isinstance(data, list):
            raise ValueError("Gemini did not return a list.")
        return data
    except Exception as exc:
        print(f"[Gemini Flash Error] {exc}")
        return _fallback_outline(story_prompt, character_name, setting, tone, art_style, panel_count)
