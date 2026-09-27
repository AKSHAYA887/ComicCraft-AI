import os
import uuid
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

try:
    from huggingface_hub import InferenceClient
except ImportError:
    InferenceClient = None

BASE_DIR = Path(__file__).resolve().parent.parent
PANELS_DIR = BASE_DIR / "static" / "panels"
PANELS_DIR.mkdir(parents=True, exist_ok=True)

HF_API_KEY = os.getenv("HF_API_KEY", "")
HF_MODEL = os.getenv("HF_MODEL", "runwayml/stable-diffusion-v1-5")

def _create_placeholder(prompt, output_path):
    width, height = 1024, 768
    image = Image.new("RGB", (width, height), (235, 240, 250))
    draw = ImageDraw.Draw(image)
    try:
        font_large = ImageFont.truetype("arial.ttf", 42)
        font_small = ImageFont.truetype("arial.ttf", 24)
    except Exception:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    draw.rectangle([20, 20, width - 20, height - 20], outline=(40, 50, 80), width=8)
    draw.text((50, 70), "ComicCraft", fill=(30, 40, 70), font=font_large)
    draw.text((50, 145), "AI Comic Panel", fill=(60, 70, 100), font=font_large)
    draw.text((50, 230), prompt[:400], fill=(50, 50, 50), font=font_small)
    draw.text((50, 680), "Configure HF_API_KEY to generate an AI illustration.", fill=(80, 80, 80), font=font_small)
    image.save(output_path, format="PNG")

def generate_image(image_prompt, panel_number=1):
    filename = f"panel_{panel_number}_{uuid.uuid4().hex[:8]}.png"
    output_path = PANELS_DIR / filename
    if not HF_API_KEY or InferenceClient is None:
        _create_placeholder(image_prompt, output_path)
        return f"/static/panels/{filename}"
    try:
        client = InferenceClient(provider="hf-inference", api_key=HF_API_KEY)
        image = client.text_to_image(prompt=image_prompt, model=HF_MODEL)
        if image is None:
            raise RuntimeError("Hugging Face returned no image.")
        image.save(output_path, format="PNG")
        return f"/static/panels/{filename}"
    except Exception as exc:
        print(f"[Image Generation Error] {exc}")
        _create_placeholder(image_prompt, output_path)
        return f"/static/panels/{filename}"
