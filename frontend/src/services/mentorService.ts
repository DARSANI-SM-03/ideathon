import {
  Mentor,
  MentorStudent,
  PriorityStudent,
  CounselingCase,
  Meeting
} from '../types';

import { API_BASE_URL } from './api';

export class MentorService {
  private static getHeaders() {
    const token = localStorage.getItem('studiq_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    };
  }

  static async getMentorProfile(): Promise<Mentor> {
    return {
      id: '50',
      name: 'Dr. Robert Vance',
      email: 'vance@studiq.edu',
      employeeId: 'MNT-2026-001',
      department: 'Computer Science',
      designation: 'Associate Professor & Senior Academic Mentor',
      phone: '+1 (555) 234-5678',
      avatar: '',
      assignedStudents: 14,
      joinedAt: '2022-08-15',
    };
  }

  static async getAssignedStudents(): Promise<MentorStudent[]> {
    try {
      const res = await fetch(`${API_BASE_URL}/mentor/students`, { headers: this.getHeaders() });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend endpoint error in mentor students service', e);
    }
    return [];
  }

  static async getPriorityQueue(): Promise<PriorityStudent[]> {
    try {
      const res = await fetch(`${API_BASE_URL}/mentor/priority-queue`, { headers: this.getHeaders() });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend endpoint error in priority queue service', e);
    }
    return [];
  }

  static async getCounselingCases(): Promise<CounselingCase[]> {
    try {
      const res = await fetch(`${API_BASE_URL}/mentor/weekly-report`, { headers: this.getHeaders() });
      if (res.ok) {
        const data = await res.json();
        if (data.report_highlights) {
          return data.report_highlights.map((item: any, idx: number) => ({
            id: `c_${idx}`,
            studentId: '1',
            student: { id: '1', name: 'Alex Mercer', department: 'Computer Science', semester: 4 },
            mentorId: '50',
            priority: 'urgent',
            reason: item.issue,
            notes: item.detail,
            status: 'scheduled',
            scheduledDate: new Date().toISOString(),
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          }));
        }
      }
    } catch (e) {}
    return [];
  }

  static async getMeetings(): Promise<Meeting[]> {
    try {
      const res = await fetch(`${API_BASE_URL}/mentor/students`, { headers: this.getHeaders() });
      if (res.ok) {
        const students = await res.json();
        // Map students requiring counseling into upcoming meetings
        return students
          .filter((s: any) => s.counselingRequired)
          .slice(0, 5)
          .map((s: any, idx: number): Meeting => ({
            id: `auto_m_${idx}`,
            mentorId: '50',
            studentId: String(s.id),
            type: 'student',
            purpose: `Academic Counseling — ${s.name}`,
            student: {
              id: String(s.id),
              name: s.name,
              department: s.department,
              semester: s.semester,
              avatar: s.avatar
            },
            date: new Date(Date.now() + (idx + 1) * 86400000).toISOString().slice(0, 10),
            time: '10:00',
            location: 'Faculty Room 204',
            notes: `Burnout Score: ${s.burnoutScore}. Intervention recommended.`,
            status: 'scheduled',
            isOnline: false,
            meetingLink: '',
            createdAt: new Date().toISOString(),
          }));
      }
    } catch (e) {
      console.warn('Backend endpoint error in mentor meetings', e);
    }
    return [];
  }
}

