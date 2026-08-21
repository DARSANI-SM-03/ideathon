from pydantic import BaseModel
from typing import List, Dict, Any

class AdminDashboardMetrics(BaseModel):
    total_students: int
    high_risk_students_count: int
    avg_focus_score: float
    avg_burnout_score: float
    department_analytics: List[Dict[str, Any]]
    institution_analytics: Dict[str, Any]
    live_monitoring_summary: Dict[str, Any]
    high_risk_students_list: List[Dict[str, Any]]
