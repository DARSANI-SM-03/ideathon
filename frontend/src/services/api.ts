import { StudentDashboardData, AdminDashboardData, ActivityLog } from '../types';
import { EMPTY_STUDENT_DASHBOARD, EMPTY_ADMIN_DASHBOARD } from './mockData';

const getApiBaseUrl = (): string => {
  const envUrl = (import.meta.env?.VITE_API_BASE_URL as string) || 'http://localhost:8000';
  const clean = envUrl.trim().replace(/\/+$/, '');
  return clean.endsWith('/api/v1') ? clean : `${clean}/api/v1`;
};

export const API_BASE_URL = getApiBaseUrl();

export class ApiService {
  public static getHeaders() {
    const token = localStorage.getItem('studiq_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    };
  }

  static async get(endpoint: string) {
    try {
      const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
      const res = await fetch(url, {
        headers: this.getHeaders()
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn(`Backend connection error fetching ${endpoint}`, e);
    }
    return null;
  }

  static async post(endpoint: string, data?: any) {
    try {
      const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
      const res = await fetch(url, {
        method: 'POST',
        headers: this.getHeaders(),
        body: data ? JSON.stringify(data) : undefined
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn(`Backend connection error posting to ${endpoint}`, e);
    }
    return null;
  }

  static async put(endpoint: string, data?: any) {
    try {
      const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
      const res = await fetch(url, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: data ? JSON.stringify(data) : undefined
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn(`Backend connection error putting to ${endpoint}`, e);
    }
    return null;
  }

  static async delete(endpoint: string) {
    try {
      const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
      const res = await fetch(url, {
        method: 'DELETE',
        headers: this.getHeaders()
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn(`Backend connection error deleting ${endpoint}`, e);
    }
    return null;
  }

  static async fetchStudentDashboard(studentId: string = 'STU-2026-001'): Promise<StudentDashboardData> {
    try {
      const res = await fetch(`${API_BASE_URL}/students/${studentId}/dashboard`, {
        headers: this.getHeaders()
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn('Backend connection error fetching student dashboard', e);
    }
    return EMPTY_STUDENT_DASHBOARD;
  }

  static async fetchAdminDashboard(): Promise<AdminDashboardData> {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/dashboard`, {
        headers: this.getHeaders()
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn('Backend connection error fetching admin dashboard', e);
    }
    return EMPTY_ADMIN_DASHBOARD;
  }

  static async assignMentor(studentIdentifier: string, mentorName: string) {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/assign-mentor`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ student_identifier: studentIdentifier, mentor_name: mentorName })
      });
      return await res.json();
    } catch (e) {
      return { status: 'error', message: 'Failed to assign mentor' };
    }
  }

  static async scheduleIntervention(studentName: string, notes?: string, date?: string) {
    try {
      const res = await fetch(`${API_BASE_URL}/mentor/schedule-intervention`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ student_name: studentName, notes, date })
      });
      return await res.json();
    } catch (e) {
      return { status: 'error', message: 'Failed to schedule intervention' };
    }
  }

  static async sendWarning(studentName: string, warningMessage?: string) {
    try {
      const res = await fetch(`${API_BASE_URL}/mentor/send-warning`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ student_name: studentName, warning_message: warningMessage })
      });
      return await res.json();
    } catch (e) {
      return { status: 'error', message: 'Failed to send warning' };
    }
  }

  static async fetchStudentActivities(studentId: number = 1): Promise<ActivityLog[]> {
    try {
      const res = await fetch(`${API_BASE_URL}/activities/student/${studentId}`, {
        headers: this.getHeaders()
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn('Backend connection error fetching student activities', e);
    }
    return [];
  }

  static async sendTelemetry(payload: {
    student_id: number;
    application_name: string;
    window_title?: string;
    website?: string;
    duration: number;
    category?: string;
  }) {
    try {
      const res = await fetch(`${API_BASE_URL}/monitoring/telemetry`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(payload)
      });
      return await res.json();
    } catch (e) {
      return { status: 'error', message: 'Failed to send telemetry to backend.' };
    }
  }
}


