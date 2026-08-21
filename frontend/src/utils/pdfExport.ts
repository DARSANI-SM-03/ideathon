import { API_BASE_URL } from '../services/api';

export const exportReportPDF = (reportType: string, studentId: number = 1) => {
  const cleanType = encodeURIComponent(reportType.toLowerCase().trim());
  const url = `${API_BASE_URL}/reports/export/pdf/${cleanType}?student_id=${studentId}`;
  window.open(url, '_blank');
};

export const exportReportCSV = (reportType: string, studentId: number = 1) => {
  const cleanType = encodeURIComponent(reportType.toLowerCase().trim());
  const url = `${API_BASE_URL}/reports/export/csv/${cleanType}?student_id=${studentId}`;
  window.open(url, '_blank');
};
