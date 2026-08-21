import { StudentDashboardData, AdminDashboardData, ActivityLog } from '../types';

export const EMPTY_STUDENT_DASHBOARD: StudentDashboardData = {
  student_id: "",
  name: "",
  department: "",
  semester: 1,
  focus_score: 0,
  burnout_score: 0,
  cgpa: 0,
  attendance: 0,
  today_productive_time_mins: 0,
  today_entertainment_time_mins: 0,
  current_status: "",
  pending_assignments_count: 0,
  avg_quiz_score: 0,
  recent_warnings: [],
  weekly_analytics: [],
  monthly_analytics: [],
  recommendations: []
};

export const MOCK_STUDENT_DASHBOARD = EMPTY_STUDENT_DASHBOARD;

export const EMPTY_ADMIN_DASHBOARD: AdminDashboardData = {
  total_students: 0,
  high_risk_students_count: 0,
  avg_focus_score: 0,
  avg_burnout_score: 0,
  department_analytics: [],
  institution_analytics: {
    total_departments: 0,
    overall_attendance_avg: 0,
    overall_cgpa_avg: 0,
    academic_health: ""
  },
  live_monitoring_summary: {
    active_applications_count: 0,
    recent_activities: []
  },
  high_risk_students_list: []
};

export const MOCK_ADMIN_DASHBOARD = EMPTY_ADMIN_DASHBOARD;
export const MOCK_ACTIVITIES: ActivityLog[] = [];

export const ARCHETYPE_STUDENT_A = { name: "Alex Mercer", focus: 94, burnout: 12 };
export const ARCHETYPE_STUDENT_B = { name: "Sophia Smith", focus: 74, burnout: 28 };
export const ARCHETYPE_STUDENT_C = { name: "David Miller", focus: 62, burnout: 78 };
export const ARCHETYPE_STUDENT_D = { name: "Ava Jackson", focus: 35, burnout: 88 };


