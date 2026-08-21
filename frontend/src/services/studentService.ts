import { StudentDashboardData, ActivityLog } from '../types';
import { EMPTY_STUDENT_DASHBOARD } from './mockData';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export class StudentService {
  private static getHeaders() {
    const token = localStorage.getItem('studiq_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    };
  }

  static async getDashboard(studentId: string = 'STU-2026-001'): Promise<StudentDashboardData> {
    try {
      const res = await fetch(`${API_BASE_URL}/students/${studentId}/dashboard`, {
        headers: this.getHeaders()
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn('Backend server connection error in student service', e);
    }
    return EMPTY_STUDENT_DASHBOARD;
  }

  static async getActivities(studentId: number = 1): Promise<ActivityLog[]> {
    try {
      const res = await fetch(`${API_BASE_URL}/activities/student/${studentId}`, {
        headers: this.getHeaders()
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn('Backend server connection error in student activities', e);
    }
    return [];
  }
}

