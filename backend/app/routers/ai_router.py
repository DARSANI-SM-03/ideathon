from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.ai.prediction_engine import ai_prediction_engine
from app.ai.central_metrics_engine import central_metrics_engine

router = APIRouter(prefix="/ai", tags=["AI Prediction & Recommendations"])

@router.get("/predict/{student_id}")
def get_student_prediction(student_id: int = 1, db: Session = Depends(get_db)):
    """Calculates AI behavioral risk predictions, probabilities, and detected patterns."""
    return ai_prediction_engine.predict_student_behavior(db, student_id)

@router.get("/recommendations")
@router.get("/recommendations/{student_id}")
def get_student_recommendations(student_id: int = 1, db: Session = Depends(get_db)):
    """Returns evidence-backed recommendations generated from real telemetry and academic records."""
    recs = central_metrics_engine.generate_evidence_based_recommendations(db, student_id)
    pred = ai_prediction_engine.predict_student_behavior(db, student_id)
    return {
        "student_id": student_id,
        "recommendations": recs,
        "raw_text_recommendations": pred["recommendations"],
        "detected_patterns": pred["detected_patterns"]
    }

@router.get("/insights/parent/{student_id}")
def get_parent_insights(student_id: int = 1, db: Session = Depends(get_db)):
    """Returns Parent AI Insights: weekly summary, positive improvements, areas of concern, and AI suggestions."""
    return ai_prediction_engine.get_parent_insights(db, student_id)

@router.get("/insights/mentor")
def get_mentor_insights(db: Session = Depends(get_db)):
    """Returns Mentor AI Insights: priority interventions, reasons, recommended actions, and risk probabilities."""
    return ai_prediction_engine.get_mentor_insights(db)

@router.get("/insights/admin")
def get_admin_insights(db: Session = Depends(get_db)):
    """Returns Admin AI Insights: campus average burnout/focus, top & risk departments, and monitoring health."""
    return ai_prediction_engine.get_admin_insights(db)

@router.get("/trends/{student_id}")
def get_behavior_trends(student_id: int = 1, period_days: int = Query(7, enum=[7, 30, 90]), db: Session = Depends(get_db)):
    """Returns historical behavior trends for 7, 30, or 90 days."""
    return ai_prediction_engine.get_behavior_trends(db, student_id, period_days)
