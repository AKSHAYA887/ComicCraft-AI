# ComicCraft - AI Comic Story Creator

AI-powered web application that transforms a story idea into a comic.

## Features
- AI story generation
- Comic panel outline
- Narration and dialogue
- AI illustrations
- Comic preview
- PDF export
- FastAPI backend
- Jinja2 frontend
- JSON API

## Run
#D:\akshaya\comicraft2026\ComicCraftAI - D drive la akshaya nu oru folder create panni zip folder extract pannu ok ah

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open: http://127.0.0.1:8000

Swagger: http://127.0.0.1:8000/docs

Health: http://127.0.0.1:8000/health

## API

POST /generate-comic/json

Example:
```json
{
  "story_prompt": "A brave fox discovers a magical forest",
  "character_name": "Foxy",
  "setting": "Fantasy Forest",
  "tone": "Funny",
  "art_style": "Comic Book",
  "panel_count": 5
}
```

Add your Gemini and Hugging Face keys to `.env`.
