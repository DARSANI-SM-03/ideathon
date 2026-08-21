import {
  ParentDashboardMetrics,
  AcademicOverview,
  DigitalBehavior,
  AIInsights,
  TimelineActivity,
  ParentControls
} from '../types';

import { API_BASE_URL } from './api';

export class ParentService {
  private static getHeaders() {
    const token = localStorage.getItem('studiq_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    };
  }

  static async getDashboardMetrics(studentId: number = 1): Promise<ParentDashboardMetrics> {
    try {
      const res = await fetch(`${API_BASE_URL}/parent/dashboard?student_id=${studentId}`, { headers: this.getHeaders() });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend endpoint connection error in parent dashboard service', e);
    }
    return {
      studentName: 'Alex Mercer',
      studentAvatar: '',
      status: {
        status: 'STUDYING',
        currentApp: 'Desktop Agent Active',
        currentCategory: 'Productive',
        lastSyncTime: new Date().toISOString(),
        sessionStartTime: new Date().toISOString(),
      },
      focusScore: 0,
      burnoutRisk: 'Low',
      burnoutScore: 0,
      attendance: 0,
      assignmentCompletion: 0,
      quizPerformance: 0,
      cgpa: 0,
      todayProductiveTime: 0,
      todayEntertainmentTime: 0,
      todayStudyTime: 0,
      weeklyFocusChange: 0,
      lastSyncTime: new Date().toISOString(),
    };
  }

  static async getAcademicOverview(): Promise<AcademicOverview> {
    try {
      const res = await fetch(`${API_BASE_URL}/parent/academic`, { headers: this.getHeaders() });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend endpoint connection error in parent academic service', e);
    }
    return {
      attendancePercent: 90,
      assignmentsCompleted: 0,
      assignmentsPending: 0,
      assignmentsTotal: 0,
      quizAverage: 0,
      cgpa: 0,
      cgpaTrend: [],
      subjects: [],
      teacherFeedback: [],
    };
  }

  static async getDigitalBehavior(): Promise<DigitalBehavior> {
    try {
      const res = await fetch(`${API_BASE_URL}/parent/dashboard`, { headers: this.getHeaders() });
      if (res.ok) {
        const data = await res.json();
        return {
          today: {
            productive: data.todayProductiveTime || 0,
            entertainment: data.todayEntertainmentTime || 0,
            educational: data.todayStudyTime || 0,
            gaming: 0,
            social: 0,
            other: 0
          },
          topApps: data.mostUsedApps || [],
          studySessions: 1,
          healthyBreaks: 1,
          weeklyTrend: []
        };
      }
    } catch (e) {
      console.warn('Backend endpoint connection error in digital behavior service', e);
    }
    return {
      today: { productive: 0, entertainment: 0, educational: 0, gaming: 0, social: 0, other: 0 },
      topApps: [],
      studySessions: 0,
      healthyBreaks: 0,
      weeklyTrend: []
    };
  }

  static async getAIInsights(): Promise<AIInsights> {
    try {
      const res = await fetch(`${API_BASE_URL}/parent/dashboard`, { headers: this.getHeaders() });
      if (res.ok) {
        const data = await res.json();
        return {
          focusScore: data.focusScore || 0,
          burnoutRisk: data.burnoutRisk || 'Low',
          burnoutScore: data.burnoutScore || 0,
          insights: (data.burnoutReasons || []).map((r: string, idx: number) => ({
            id: `ins_${idx}`,
            type: 'neutral',
            message: r,
            change: 0
          })),
          recommendations: [],
          generatedAt: new Date().toISOString()
        };
      }
    } catch (e) {
      console.warn('Backend endpoint connection error in parent insights service', e);
    }
    return {
      focusScore: 0,
      burnoutRisk: 'Low',
      burnoutScore: 0,
      insights: [],
      recommendations: [],
      generatedAt: new Date().toISOString(),
    };
  }

  static async getTimelineActivities(): Promise<TimelineActivity[]> {
    try {
      const res = await fetch(`${API_BASE_URL}/parent/dashboard`, { headers: this.getHeaders() });
      if (res.ok) {
        const data = await res.json();
        return data.dailyTimeline || [];
      }
    } catch (e) {}
    return [];
  }

  static async getControls(): Promise<ParentControls> {
    return {
      dailyEntertainmentLimitMinutes: 90,
      weekendEntertainmentLimitMinutes: 180,
      studyScheduleStart: '08:30',
      studyScheduleEnd: '21:30',
      allowedApps: [],
      blockedApps: [],
      specialPermissions: [],
    };
  }
}

