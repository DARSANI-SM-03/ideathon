// ============================================================
// StudIQ Unified Platform — TypeScript Definitions
// ============================================================

export type UserRole = 'student' | 'admin' | 'mentor' | 'parent' | 'teacher';

export interface UserProfile {
  id: number;
  user_identifier: string;
  name: string;
  email: string;
  role: UserRole;
  department?: string;
}

// Student Dashboard Types
export interface StudentDashboardData {
  student_id: string;
  name: string;
  department: string;
  semester: number;
  focus_score: number;
  burnout_score: number;
  cgpa: number;
  attendance: number;
  today_productive_time_mins: number;
  today_entertainment_time_mins: number;
  current_status: string;
  pending_assignments_count: number;
  avg_quiz_score: number;
  recent_warnings: WarningItem[];
  weekly_analytics: WeeklyMetric[];
  monthly_analytics: WeeklyMetric[];
  recommendations: string[];
}

export interface WarningItem {
  id: number;
  title: string;
  message: string;
  severity: 'Low' | 'Medium' | 'High' | 'Critical';
  trigger_source: string;
  created_at: string;
}

export interface WeeklyMetric {
  day: string;
  focus: number;
  burnout: number;
  study_hours: number;
}

// Admin Dashboard Types
export interface AdminDashboardData {
  total_students: number;
  high_risk_students_count: number;
  avg_focus_score: number;
  avg_burnout_score: number;
  department_analytics: DepartmentMetric[];
  institution_analytics: {
    total_departments: number;
    overall_attendance_avg: number;
    overall_cgpa_avg: number;
    academic_health: string;
  };
  live_monitoring_summary: {
    active_applications_count: number;
    recent_activities: LiveActivity[];
  };
  high_risk_students_list: HighRiskStudent[];
}

export interface DepartmentMetric {
  department: string;
  student_count: number;
  avg_focus_score: number;
  avg_burnout_score: number;
  avg_cgpa: number;
}

export interface HighRiskStudent {
  id: number;
  student_id: string;
  name: string;
  department: string;
  semester: number;
  focus_score: number;
  burnout_score: number;
  risk_level: string;
  attendance: number;
  cgpa: number;
}

export interface LiveActivity {
  activity_id: number;
  student_id: number;
  application_name: string;
  window_title?: string;
  category: string;
  duration_mins: number;
}

export interface ActivityLog {
  activity_id: number;
  student_id: number;
  application_name: string;
  window_title?: string;
  website?: string;
  category: 'Study' | 'Coding' | 'Research' | 'Entertainment' | 'Social Media' | 'Gaming' | 'Utility';
  start_time: string;
  end_time: string;
  duration: number;
}

// ============================================================
// PARENT PORTAL TYPES
// ============================================================

export interface ParentUser {
  id: string;
  name: string;
  email: string;
  phone: string;
  avatar?: string;
  relationship: 'Father' | 'Mother' | 'Guardian';
  students: StudentLink[];
}

export interface StudentLink {
  id: string;
  name: string;
  rollNumber: string;
  department: string;
  semester: number;
  section: string;
  avatar?: string;
}

export type StudentStatusType =
  | 'STUDYING'
  | 'HEALTHY_BREAK'
  | 'PRODUCTIVE'
  | 'ENTERTAINMENT'
  | 'OFFLINE';

export interface ParentStudentStatus {
  status: StudentStatusType;
  currentApp: string;
  currentCategory: string;
  lastSyncTime: string;
  sessionStartTime?: string;
}

export interface ParentDashboardMetrics {
  studentName: string;
  studentAvatar?: string;
  status: ParentStudentStatus;
  focusScore: number;
  burnoutRisk: 'Low' | 'Moderate' | 'High' | 'Critical';
  burnoutScore: number;
  attendance: number;
  assignmentCompletion: number;
  quizPerformance: number;
  cgpa: number;
  todayProductiveTime: number;
  todayEntertainmentTime: number;
  todayStudyTime: number;
  weeklyFocusChange: number;
  lastSyncTime: string;
}

export interface SubjectPerformance {
  subject: string;
  code: string;
  attendance: number;
  grade: string;
  marks: number;
  maxMarks: number;
  quizAvg: number;
}

export interface CGPATrendPoint {
  semester: string;
  cgpa: number;
}

export interface TeacherFeedback {
  id: string;
  teacher: string;
  subject: string;
  message: string;
  date: string;
  sentiment: 'positive' | 'neutral' | 'negative';
}

export interface AcademicOverview {
  attendancePercent: number;
  assignmentsCompleted: number;
  assignmentsPending: number;
  assignmentsTotal: number;
  quizAverage: number;
  cgpa: number;
  cgpaTrend: CGPATrendPoint[];
  subjects: SubjectPerformance[];
  teacherFeedback: TeacherFeedback[];
}

export interface AppUsageEntry {
  appName: string;
  category: 'Educational' | 'Entertainment' | 'Productive' | 'Gaming' | 'Social' | 'Other';
  timeMinutes: number;
  iconEmoji?: string;
}

export interface DailyTimeBreakdown {
  productive: number;
  entertainment: number;
  educational: number;
  gaming: number;
  social: number;
  other: number;
}

export interface WeeklyFocusPoint {
  day: string;
  focusScore: number;
  productiveTime: number;
  entertainmentTime: number;
}

export interface DigitalBehavior {
  today: DailyTimeBreakdown;
  topApps: AppUsageEntry[];
  studySessions: number;
  healthyBreaks: number;
  weeklyTrend: WeeklyFocusPoint[];
}

export type RiskLevel = 'Low' | 'Moderate' | 'High' | 'Critical';

export interface InsightCard {
  id: string;
  type: 'positive' | 'neutral' | 'warning' | 'danger';
  message: string;
  metric?: string;
  change?: number;
}

export interface Recommendation {
  id: string;
  priority: 'high' | 'medium' | 'low';
  message: string;
  category: 'study' | 'health' | 'digital' | 'academic';
}

export interface AIInsights {
  focusScore: number;
  burnoutRisk: RiskLevel;
  burnoutScore: number;
  insights: InsightCard[];
  recommendations: Recommendation[];
  generatedAt: string;
}

export type ActivityCategory =
  | 'Educational'
  | 'Entertainment'
  | 'Productive'
  | 'Gaming'
  | 'Study'
  | 'Break'
  | 'Assignment';

export interface TimelineActivity {
  id: string;
  time: string;
  appName: string;
  category: ActivityCategory;
  duration?: number;
  note?: string;
}

export interface AppPermission {
  appName: string;
  allowed: boolean;
  category?: string;
  restriction?: string;
  weekendOnly?: boolean;
}

export interface ParentControls {
  dailyEntertainmentLimitMinutes: number;
  weekendEntertainmentLimitMinutes: number;
  studyScheduleStart: string;
  studyScheduleEnd: string;
  allowedApps: AppPermission[];
  blockedApps: AppPermission[];
  specialPermissions: AppPermission[];
}

export type NotificationType =
  | 'entertainment_limit'
  | 'warnings_ignored'
  | 'focus_decreased'
  | 'burnout_risk'
  | 'weekly_report'
  | 'assignment_overdue'
  | 'attendance_concern'
  | 'late_night_study';

export interface Notification {
  id: string;
  type: NotificationType | string;
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  severity?: 'info' | 'warning' | 'danger' | 'success';
}

export type ReportType = 'daily' | 'weekly' | 'monthly' | 'semester';

export interface ReportData {
  type: ReportType;
  period: string;
  generatedAt: string;
  summary: {
    totalStudyTime: number;
    avgFocusScore: number;
    attendancePercent: number;
    assignmentsCompleted: number;
    entertainmentTime: number;
    burnoutEvents: number;
  };
  chartData: {
    labels: string[];
    focusScores: number[];
    studyTimes: number[];
    entertainmentTimes: number[];
  };
}

export type MeetingStatus = 'Pending' | 'Confirmed' | 'Declined' | 'Completed' | 'scheduled' | 'cancelled';

export interface MeetingRequest {
  id: string;
  reason: string;
  preferredDate: string;
  preferredTime: string;
  teacherName?: string;
  mentorName?: string;
  status: MeetingStatus;
  createdAt: string;
  notes?: string;
}

export interface NotificationPreferences {
  entertainmentAlert: boolean;
  burnoutAlert: boolean;
  focusDecreaseAlert: boolean;
  attendanceAlert: boolean;
  assignmentOverdue: boolean;
  weeklyReport: boolean;
  lateNightAlert: boolean;
}

export interface ParentProfile {
  id: string;
  name: string;
  email: string;
  phone: string;
  relationship: string;
  avatar?: string;
  linkedStudents: StudentLink[];
  notificationPreferences: NotificationPreferences;
}

// ============================================================
// MENTOR PORTAL TYPES
// ============================================================

export type BurnoutRisk = 'critical' | 'high' | 'medium' | 'low';
export type StudentStatus = 'online' | 'studying' | 'entertainment' | 'offline';
export type CounselingStatus = 'pending' | 'scheduled' | 'completed' | 'cancelled';
export type MeetingType = 'student' | 'parent' | 'joint';

export interface Mentor {
  id: string;
  name: string;
  email: string;
  employeeId: string;
  department: string;
  designation: string;
  phone?: string;
  avatar?: string;
  assignedStudents: number;
  joinedAt: string;
}

export interface MentorStudent {
  id: string;
  name: string;
  email: string;
  studentId: string;
  department: string;
  semester: number;
  avatar?: string;
  phone?: string;
  parentPhone?: string;
  enrollmentYear?: number;
  attendance: number;
  cgpa: number;
  focusScore: number;
  burnoutRisk: BurnoutRisk;
  burnoutScore: number;
  currentStatus: StudentStatus;
  lastActive: string;
  assignmentCompletion: number;
  quizAverage: number;
  totalStudyHours: number;
  entertainmentHours: number;
  isActive: boolean;
  counselingRequired: boolean;
  mentorId: string;
}

export type PriorityCategory =
  | 'critical_burnout'
  | 'high_burnout'
  | 'low_focus'
  | 'low_attendance'
  | 'pending_assignments'
  | 'inactive';

export interface PriorityStudent {
  student: MentorStudent;
  categories: PriorityCategory[];
  priorityScore: number;
  reason: string;
}

export interface CounselingCase {
  id: string;
  studentId: string;
  student: Pick<MentorStudent, 'id' | 'name' | 'department' | 'semester' | 'avatar'>;
  mentorId: string;
  priority: 'urgent' | 'high' | 'medium' | 'low';
  reason: string;
  notes?: string;
  status: CounselingStatus;
  scheduledDate?: string;
  completedDate?: string;
  counselorAssigned?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Meeting {
  id: string;
  mentorId: string;
  studentId: string;
  student: Pick<MentorStudent, 'id' | 'name' | 'department' | 'semester' | 'avatar'>;
  type: MeetingType;
  purpose: string;
  date: string;
  time: string;
  location: string;
  isOnline: boolean;
  meetingLink?: string;
  notes?: string;
  status: MeetingStatus;
  createdAt: string;
}

export interface PrivateNote {
  id: string;
  studentId: string;
  mentorId: string;
  content: string;
  isConfidential: boolean;
  createdAt: string;
  updatedAt: string;
}

export type MessageSender = 'parent' | 'student' | 'mentor' | 'system' | 'admin';

export interface Message {
  id: string;
  conversationId: string;
  sender: MessageSender;
  senderName: string;
  content: string;
  timestamp: string;
  read: boolean;
}

export interface Conversation {
  id: string;
  type: 'student' | 'mentor' | 'parent';
  participantName: string;
  participantAvatar?: string;
  lastMessage: string;
  lastMessageTime: string;
  unreadCount: number;
}
