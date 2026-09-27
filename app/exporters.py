import uuid
from pathlib import Path
from fpdf import FPDF

BASE_DIR = Path(__file__).resolve().parent.parent
EXPORT_DIR = BASE_DIR / "static" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

def _clean_text(text):
    if not text:
        return ""
    replacements = {"—": "-", "–": "-", "“": '"', "”": '"', "‘": "'", "’": "'", "…": "...", "•": "-"}
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("latin-1", "replace").decode("latin-1")

def save_pdf(layout, title="ComicCraft Comic"):
    filename = f"comiccraft_{uuid.uuid4().hex[:10]}.pdf"
    output_path = EXPORT_DIR / filename
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_title(_clean_text(title))
    for panel in layout:
        pdf.add_page()
        pdf.set_font("Arial", "B", 20)
        pdf.multi_cell(0, 12, _clean_text(f"Panel {panel['panel_number']}: {panel['title']}"))
        pdf.ln(3)
        image_path = panel.get("image_path")
        if image_path:
            relative = image_path[len("/static/"):] if image_path.startswith("/static/") else image_path
            full_image_path = BASE_DIR / "static" / relative
            if full_image_path.exists():
                try:
                    pdf.image(str(full_image_path), x=15, y=45, w=180, h=110)
                except Exception as exc:
                    print(f"PDF image error: {exc}")
        pdf.ln(115)
        pdf.set_font("Arial", "I", 11)
        pdf.multi_cell(0, 7, _clean_text(panel.get("scene_description", "")))
        for label, key in [("Caption", "caption"), ("Narration", "narration"), ("Dialogue", "dialogue")]:
            if panel.get(key):
                pdf.ln(2)
                pdf.set_font("Arial", "B", 11)
                pdf.multi_cell(0, 7, f"{label}: " + _clean_text(panel[key]))
    pdf.output(str(output_path))
    return f"/static/exports/{filename}"
