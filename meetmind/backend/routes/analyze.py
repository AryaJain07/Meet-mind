import os
import json
import requests
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from database.models import get_db, Meeting

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"


# ---------- Request / Response Schemas ----------

class AnalyzeRequest(BaseModel):
    transcript: str
    options: Optional[dict] = {
        "summary": True,
        "actions": True,
        "decisions": True,
        "sentiment": False,
        "participants": False,
    }


class AnalyzeResponse(BaseModel):
    id: int
    summary: Optional[str]
    action_items: Optional[list]
    key_points: Optional[list]
    sentiment: Optional[dict]
    participants: Optional[list]
    meeting_meta: Optional[dict]


# ---------- Helper: Call Gemini ----------

def call_gemini(transcript: str, requested_sections: List[str]) -> dict:
    system_prompt = """You are an expert meeting analyst. Analyze the meeting transcript and return a JSON object with exactly these keys (only include keys that are in the requested_sections list):

- summary: A 2-3 sentence executive summary of the meeting.
- action_items: Array of objects with { task: string, owner: string, priority: "high"|"medium"|"low" }.
- key_points: Array of strings (important decisions or insights, max 5).
- sentiment: Object with { positive: number (0-100), neutral: number (0-100), negative: number (0-100) } adding up to 100.
- participants: Array of participant names mentioned.
- meeting_meta: Object with { duration_estimate: string, topic: string, meeting_type: string }.

Always include meeting_meta. Return ONLY valid JSON. No markdown, no code blocks, no extra text. Start directly with { and end with }."""

    user_prompt = f"Requested sections: {', '.join(requested_sections)}, meeting_meta\n\nTranscript:\n{transcript}"

    payload = {
        "contents": [{"parts": [{"text": system_prompt + "\n\n" + user_prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 2000,
            "responseMimeType": "application/json"
        }
    }

    response = requests.post(GEMINI_URL, json=payload, timeout=30)
    response.raise_for_status()

    data = response.json()
    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
    clean = raw_text.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip()
    return json.loads(clean)


# ---------- Helper: Extract text from uploaded file ----------

def extract_text_from_file(file: UploadFile) -> str:
    content = file.file.read()
    filename = file.filename.lower()

    # Plain text file (.txt)
    if filename.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")

    # PDF file
    elif filename.endswith(".pdf"):
        try:
            import io
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except ImportError:
            raise HTTPException(status_code=400, detail="PyPDF2 not installed. Run: pip install PyPDF2")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not read PDF: {str(e)}")

    else:
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported")


# ---------- Routes ----------

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_meeting(req: AnalyzeRequest, db: Session = Depends(get_db)):
    if not req.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")

    opts = req.options or {}
    requested_sections = []
    if opts.get("summary"):      requested_sections.append("summary")
    if opts.get("actions"):      requested_sections.append("action_items")
    if opts.get("decisions"):    requested_sections.append("key_points")
    if opts.get("sentiment"):    requested_sections.append("sentiment")
    if opts.get("participants"): requested_sections.append("participants")

    if not requested_sections:
        raise HTTPException(status_code=400, detail="Select at least one analysis option")

    try:
        result = call_gemini(req.transcript, requested_sections)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")

    meta = result.get("meeting_meta", {})

    # Save to database
    meeting = Meeting(
        title=meta.get("topic", "Untitled Meeting"),
        transcript=req.transcript,
        summary=result.get("summary"),
        action_items=json.dumps(result.get("action_items", [])),
        key_points=json.dumps(result.get("key_points", [])),
        participants=json.dumps(result.get("participants", [])),
        sentiment=json.dumps(result.get("sentiment", {})),
        meeting_type=meta.get("meeting_type"),
        duration_estimate=meta.get("duration_estimate"),
        topic=meta.get("topic"),
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    return AnalyzeResponse(
        id=meeting.id,
        summary=result.get("summary"),
        action_items=result.get("action_items"),
        key_points=result.get("key_points"),
        sentiment=result.get("sentiment"),
        participants=result.get("participants"),
        meeting_meta=meta,
    )


# ---------- File Upload Route ----------

@router.post("/upload", response_model=AnalyzeResponse)
async def upload_and_analyze(
    file: UploadFile = File(...),
    options: str = Form(default='{"summary":true,"actions":true,"decisions":true,"sentiment":false,"participants":false}'),
    db: Session = Depends(get_db)
):
    # Extract text from file
    transcript = extract_text_from_file(file)

    if not transcript.strip():
        raise HTTPException(status_code=400, detail="File is empty or could not be read")

    # Parse options
    try:
        opts = json.loads(options)
    except:
        opts = {"summary": True, "actions": True, "decisions": True}

    requested_sections = []
    if opts.get("summary"):      requested_sections.append("summary")
    if opts.get("actions"):      requested_sections.append("action_items")
    if opts.get("decisions"):    requested_sections.append("key_points")
    if opts.get("sentiment"):    requested_sections.append("sentiment")
    if opts.get("participants"): requested_sections.append("participants")

    if not requested_sections:
        requested_sections = ["summary", "action_items", "key_points"]

    try:
        result = call_gemini(transcript, requested_sections)
    except Exception as e:
        import traceback
        print("GEMINI ERROR:", traceback.format_exc())
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")

    meta = result.get("meeting_meta", {})

    meeting = Meeting(
        title=meta.get("topic", file.filename or "Uploaded Meeting"),
        transcript=transcript,
        summary=result.get("summary"),
        action_items=json.dumps(result.get("action_items", [])),
        key_points=json.dumps(result.get("key_points", [])),
        participants=json.dumps(result.get("participants", [])),
        sentiment=json.dumps(result.get("sentiment", {})),
        meeting_type=meta.get("meeting_type"),
        duration_estimate=meta.get("duration_estimate"),
        topic=meta.get("topic"),
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    return AnalyzeResponse(
        id=meeting.id,
        summary=result.get("summary"),
        action_items=result.get("action_items"),
        key_points=result.get("key_points"),
        sentiment=result.get("sentiment"),
        participants=result.get("participants"),
        meeting_meta=meta,
    )
