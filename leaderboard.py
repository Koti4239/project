# =====================================================
# LEADERBOARD API (FASTAPI)
# =====================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import SessionLocal
from models.leaderboard import Leaderboard
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

# =====================================================
# DATABASE CONNECTION
# =====================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =====================================================
# REQUEST MODEL
# =====================================================
class LeaderboardUpdate(BaseModel):
    user_name: str
    aptitude: float = 0
    coding: float = 0
    communication: float = 0
    hr: float = 0
    resume: float = 0

# =====================================================
# UPDATE / CREATE USER SCORE
# =====================================================
@router.post("/update")
def update_leaderboard(data: LeaderboardUpdate, db: Session = Depends(get_db)):

    # Calculate total score
    total_score = (
        data.aptitude +
        data.coding +
        data.communication +
        data.hr +
        data.resume
    )

    # Check if user exists
    user = db.query(Leaderboard).filter(
        Leaderboard.user_name == data.user_name
    ).first()

    if user:
        # Update existing user
        user.aptitude_score = data.aptitude
        user.coding_score = data.coding
        user.communication_score = data.communication
        user.hr_score = data.hr
        user.resume_score = data.resume
        user.total_score = total_score
        user.last_updated = datetime.utcnow()

    else:
        # Create new user
        user = Leaderboard(
            user_name=data.user_name,
            aptitude_score=data.aptitude,
            coding_score=data.coding,
            communication_score=data.communication,
            hr_score=data.hr,
            resume_score=data.resume,
            total_score=total_score,
            last_updated=datetime.utcnow()
        )
        db.add(user)

    db.commit()

    return {
        "message": "Leaderboard updated successfully",
        "total_score": total_score
    }

# =====================================================
# GET TOP LEADERBOARD (WITH BADGES)
# =====================================================
@router.get("/top")
def get_leaderboard(db: Session = Depends(get_db)):

    users = db.query(Leaderboard).order_by(
        desc(Leaderboard.total_score)
    ).all()

    result = []

    for i, user in enumerate(users):

        # Assign medals
        if i == 0:
            badge = "🥇 Gold"
        elif i == 1:
            badge = "🥈 Silver"
        elif i == 2:
            badge = "🥉 Bronze"
        else:
            badge = None

        result.append({
            "rank": i + 1,
            "user_name": user.user_name,
            "total_score": user.total_score,
            "badge": badge,
            "last_updated": user.last_updated
        })

    return result

# =====================================================
# GET USER RANK
# =====================================================
@router.get("/rank/{username}")
def get_user_rank(username: str, db: Session = Depends(get_db)):

    users = db.query(Leaderboard).order_by(
        desc(Leaderboard.total_score)
    ).all()

    for index, user in enumerate(users):
        if user.user_name == username:
            return {
                "user_name": username,
                "rank": index + 1,
                "total_score": user.total_score
            }

    raise HTTPException(status_code=404, detail="User not found")

# =====================================================
# WEEKLY LEADERBOARD
# =====================================================
@router.get("/weekly")
def weekly_leaderboard(db: Session = Depends(get_db)):

    last_week = datetime.utcnow() - timedelta(days=7)

    users = db.query(Leaderboard).filter(
        Leaderboard.last_updated >= last_week
    ).order_by(desc(Leaderboard.total_score)).all()

    return users

# =====================================================
# MODULE-WISE RANKING
# =====================================================
@router.get("/module/{module_name}")
def module_ranking(module_name: str, db: Session = Depends(get_db)):

    column_map = {
        "coding": Leaderboard.coding_score,
        "aptitude": Leaderboard.aptitude_score,
        "communication": Leaderboard.communication_score,
        "hr": Leaderboard.hr_score,
        "resume": Leaderboard.resume_score
    }

    # Validate module
    if module_name not in column_map:
        raise HTTPException(status_code=400, detail="Invalid module name")

    users = db.query(Leaderboard).order_by(
        desc(column_map[module_name])
    ).all()

    return [
        {
            "rank": i + 1,
            "user_name": u.user_name,
            "score": getattr(u, f"{module_name}_score")
        }
        for i, u in enumerate(users)
    ]