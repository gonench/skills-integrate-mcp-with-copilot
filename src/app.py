"""Mergington High School Activities API backed by SQLite + SQLAlchemy

This module uses SQLAlchemy models in `src/models.py` and provides the same
public endpoints as before but backed by a persistent database.
"""

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from .models import create_tables, get_session, Activity, Participant

app = FastAPI(
    title="Mergington High School API",
    description="API for viewing and signing up for extracurricular activities (persistent DB)",
)

# Mount static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")


@app.on_event("startup")
def startup_event():
    # Create DB tables when the app starts
    create_tables()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    session = get_session()
    try:
        activities = session.query(Activity).all()
        result = {}
        for a in activities:
            result[a.name] = {
                "description": a.description,
                "schedule": a.schedule,
                "max_participants": a.max_participants,
                "participants": [p.email for p in a.participants],
            }
        return result
    finally:
        session.close()


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    session = get_session()
    try:
        activity = session.query(Activity).filter(Activity.name == activity_name).first()
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        # Check if participant exists or create
        participant = session.query(Participant).filter(Participant.email == email).first()
        if participant and participant in activity.participants:
            raise HTTPException(status_code=400, detail="Student is already signed up")

        if activity.max_participants and len(activity.participants) >= activity.max_participants:
            raise HTTPException(status_code=400, detail="Activity is full")

        if not participant:
            participant = Participant(email=email)
            session.add(participant)

        activity.participants.append(participant)
        session.add(activity)
        session.commit()
        return {"message": f"Signed up {email} for {activity_name}"}
    finally:
        session.close()


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    session = get_session()
    try:
        activity = session.query(Activity).filter(Activity.name == activity_name).first()
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        participant = session.query(Participant).filter(Participant.email == email).first()
        if not participant or participant not in activity.participants:
            raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

        activity.participants.remove(participant)
        session.add(activity)
        session.commit()
        return {"message": f"Unregistered {email} from {activity_name}"}
    finally:
        session.close()


if __name__ == "__main__":
    # Allow running `python -m uvicorn src.app:app --reload` or similar; keep a simple runner
    import uvicorn

    uvicorn.run("src.app:app", host="127.0.0.1", port=8000, reload=True)
