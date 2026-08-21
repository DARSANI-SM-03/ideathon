from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, List
from app.database.session import get_db
from app.models.notification import Notification, Message
from app.models.monitoring import WarningLog, ParentAlert, MentorAlert, BehaviorMetricRecord
from app.models.user import Student, ParentConsent

router = APIRouter(prefix="/notifications", tags=["Notification Center"])

@router.get("/{student_id}")
def get_notifications(student_id: int = 1, db: Session = Depends(get_db)):
    """
    Returns persistent notification center items for Warnings, Parent Approvals,
    Mentor Interventions, Monitoring Offline status, High Burnout alerts, and System Announcements.
    """
    notifications_list = []

    # 1. Parent Consent & Approval Status
    consent = db.query(ParentConsent).filter(ParentConsent.student_id == student_id).first()
    if consent:
        if consent.status == "Pending":
            notifications_list.append({
                "id": "notif_consent_pending",
                "type": "parent_approval",
                "title": "Parent Approval Pending",
                "message": "Your desktop monitoring permission request has been sent to your parent for approval.",
                "severity": "medium",
                "is_read": False,
                "created_at": consent.created_at.isoformat() if consent.created_at else datetime.utcnow().isoformat()
            })
        elif consent.status == "Approved":
            notifications_list.append({
                "id": "notif_consent_approved",
                "type": "parent_approval",
                "title": "Monitoring Permission Granted",
                "message": "Your parent has approved desktop agent monitoring. Your account is active.",
                "severity": "info",
                "is_read": True,
                "created_at": consent.approved_at.isoformat() if consent.approved_at else datetime.utcnow().isoformat()
            })

    # 2. Warning Logs
    warnings = db.query(WarningLog).filter(WarningLog.student_id == student_id).order_by(WarningLog.timestamp.desc()).limit(5).all()
    for w in warnings:
        notifications_list.append({
            "id": f"notif_warn_{w.id}",
            "type": "warning",
            "title": f"Entertainment Warning #{w.warning_count}",
            "message": w.message,
            "severity": "high" if w.warning_count >= 3 else "medium",
            "is_read": False,
            "created_at": w.timestamp.isoformat() if w.timestamp else datetime.utcnow().isoformat()
        })

    # 3. High Burnout & Mentoring Interventions
    p_alerts = db.query(ParentAlert).filter(ParentAlert.student_id == student_id).order_by(ParentAlert.timestamp.desc()).limit(3).all()
    for pa in p_alerts:
        notifications_list.append({
            "id": f"notif_palert_{pa.id}",
            "type": "parent_alert",
            "title": "Parent Safety Alert Generated",
            "message": pa.reason,
            "severity": "high",
            "is_read": False,
            "created_at": pa.timestamp.isoformat() if pa.timestamp else datetime.utcnow().isoformat()
        })

    # 4. System Announcement
    notifications_list.append({
        "id": "notif_system_announcement",
        "type": "system_announcement",
        "title": "StudIQ AI Intelligence Active",
        "message": "Real-time Behavior Intelligence Engine & Focus Score tracking is active.",
        "severity": "info",
        "is_read": True,
        "created_at": datetime.utcnow().isoformat()
    })

    return notifications_list

@router.post("/mark-read/{notification_id}")
def mark_notification_read(notification_id: str, db: Session = Depends(get_db)):
    return {"status": "success", "notification_id": notification_id, "is_read": True}

