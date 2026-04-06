import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from database.models import get_db, Meeting

router = APIRouter()


# ---------- Schemas ----------

class MeetingOut(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    meeting_type: Optional[str]
    duration_estimate: Optional[str]
    topic: Optional[str]
    participants: Optional[list]
    action_items: Optional[list]
    key_points: Optional[list]
    sentiment: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Routes ----------

@router.get("/meetings", response_model=List[MeetingOut])
def get_all_meetings(db: Session = Depends(get_db)):
    meetings = db.query(Meeting).order_by(Meeting.created_at.desc()).all()
    result = []
    for m in meetings:
        result.append(MeetingOut(
            id=m.id,
            title=m.title or "Untitled",
            summary=m.summary,
            meeting_type=m.meeting_type,
            duration_estimate=m.duration_estimate,
            topic=m.topic,
            participants=json.loads(m.participants) if m.participants else [],
            action_items=json.loads(m.action_items) if m.action_items else [],
            key_points=json.loads(m.key_points) if m.key_points else [],
            sentiment=json.loads(m.sentiment) if m.sentiment else {},
            created_at=m.created_at,
        ))
    return result


@router.get("/meetings/{meeting_id}", response_model=MeetingOut)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    m = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return MeetingOut(
        id=m.id,
        title=m.title or "Untitled",
        summary=m.summary,
        meeting_type=m.meeting_type,
        duration_estimate=m.duration_estimate,
        topic=m.topic,
        participants=json.loads(m.participants) if m.participants else [],
        action_items=json.loads(m.action_items) if m.action_items else [],
        key_points=json.loads(m.key_points) if m.key_points else [],
        sentiment=json.loads(m.sentiment) if m.sentiment else {},
        created_at=m.created_at,
    )


@router.delete("/meetings/{meeting_id}")
def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    m = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Meeting not found")
    db.delete(m)
    db.commit()
    return {"message": f"Meeting {meeting_id} deleted successfully"}
