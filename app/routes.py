from pathlib import Path
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from .models import PromptRequest
from .gemini_flash import generate_outline
from .gemini_pro import generate_story
from .image_generator import generate_image
from .layout_builder import build_comic_layout
from .exporters import save_pdf

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

def create_comic(story_prompt, character_name, setting, tone, art_style, panel_count):
    outline = generate_outline(story_prompt, character_name, setting, tone, art_style, panel_count)
    stories = generate_story(outline, character_name, tone)
    image_paths = [
        generate_image(panel.get("image_prompt", ""), panel.get("panel_number", i + 1))
        for i, panel in enumerate(outline)
    ]
    layout = build_comic_layout(outline, stories, image_paths)
    title = f"{character_name}'s Comic Adventure"
    pdf_path = save_pdf(layout, title)
    return {"title": title, "layout": layout, "pdf_path": pdf_path}

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
    request=request,
    name="index.html"
)

@router.post("/generate", response_class=HTMLResponse)
async def generate_comic(request: Request,
                         story_prompt: str = Form(...),
                         character_name: str = Form("Alex"),
                         setting: str = Form("Fantasy Forest"),
                         tone: str = Form("Funny"),
                         art_style: str = Form("Comic Book"),
                         panel_count: int = Form(5)):
    try:
        panel_count = max(1, min(panel_count, 8))
        result = create_comic(story_prompt, character_name, setting, tone, art_style, panel_count)
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "title": result["title"],
                "layout": result["layout"],
                "pdf_path": result["pdf_path"]
            }
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": f"Something went wrong: {str(exc)}"
            },
            status_code=500
        )

@router.post("/generate-comic/json")
async def generate_comic_json(data: PromptRequest):
    try:
        result = create_comic(data.story_prompt, data.character_name, data.setting,
                              data.tone, data.art_style, data.panel_count)
        return JSONResponse({"success": True, "title": result["title"],
                             "panels": result["layout"], "pdf_path": result["pdf_path"]})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/test-image")
async def test_image():
    return {"success": True, "image_path": generate_image(
        "A cute superhero fox standing in a magical forest, comic book style, colorful, cinematic lighting", 999)}

@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, pdf_path: str = ""):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "pdf_path": pdf_path
        }
    )
