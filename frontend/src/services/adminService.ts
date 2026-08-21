import { AdminDashboardData } from '../types';
import { EMPTY_ADMIN_DASHBOARD } from './mockData';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export class AdminService {
  private static getHeaders() {
    const token = localStorage.getItem('studiq_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    };
  }

  static async getDashboard(): Promise<AdminDashboardData> {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/dashboard`, {
        headers: this.getHeaders()
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn('Backend server connection error in admin service', e);
    }
    return EMPTY_ADMIN_DASHBOARD;
  }
}

