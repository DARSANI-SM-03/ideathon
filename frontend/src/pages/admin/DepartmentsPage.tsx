import React, { useEffect, useState } from 'react';
import { DepartmentComparisonChart } from '../../charts/DepartmentComparisonChart';
import { Building } from 'lucide-react';
import { API_BASE_URL } from '../../services/api';

interface DeptData {
  name: string;
  students: number;
  focus: number;
  burnout: number;
  cgpa: number;
}

const FALLBACK_DEPTS: DeptData[] = [
  { name: 'Computer Science', students: 55, focus: 82.4, burnout: 28.1, cgpa: 3.52 },
  { name: 'Electronics & Comm', students: 42, focus: 76.5, burnout: 34.2, cgpa: 3.38 },
  { name: 'Mechanical Eng', students: 38, focus: 75.1, burnout: 33.8, cgpa: 3.29 },
  { name: 'Electrical Eng', students: 35, focus: 79.0, burnout: 29.5, cgpa: 3.44 },
  { name: 'Civil Eng', students: 30, focus: 74.8, burnout: 35.6, cgpa: 3.25 }
];

export const DepartmentsPage: React.FC = () => {
  const [departments, setDepartments] = useState<DeptData[]>(FALLBACK_DEPTS);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/admin/analytics`, {
      headers: {
        'Content-Type': 'application/json',
        ...(localStorage.getItem('studiq_token') ? { Authorization: `Bearer ${localStorage.getItem('studiq_token')}` } : {})
      }
    })
      .then(r => r.json())
      .then((data: any) => {
        // analytics endpoint returns department breakdown in dept_breakdown key
        const depts: DeptData[] = (data.dept_breakdown || []).map((d: any) => ({
          name: d.department,
          students: d.student_count ?? 0,
          focus: parseFloat((d.avg_focus_score ?? 0).toFixed(1)),
          burnout: parseFloat((d.avg_burnout_score ?? 0).toFixed(1)),
          cgpa: parseFloat((d.avg_cgpa ?? 0).toFixed(2)),
        }));
        if (depts.length > 0) setDepartments(depts);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <Building className="w-6 h-6 text-brand-400" />
          Department Intelligence Analytics
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Comparative analysis of Focus Scores, Burnout Risk, and CGPA across academic departments.
          {loading && <span className="ml-2 text-brand-400 animate-pulse">Loading live data…</span>}
        </p>
      </div>

      <div className="glass-card rounded-2xl p-6 border border-slate-800">
        <h3 className="text-base font-bold text-slate-100 mb-4">Department Focus & Burnout Breakdown</h3>
        <DepartmentComparisonChart data={departments.map((d) => ({
          department: d.name,
          student_count: d.students,
          avg_focus_score: d.focus,
          avg_burnout_score: d.burnout,
          avg_cgpa: d.cgpa
        }))} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {departments.map((d, i) => (
          <div key={i} className="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-slate-100">{d.name}</h3>
              <span className="text-xs font-mono text-brand-400">{d.students} Students</span>
            </div>

            <div className="space-y-2 text-xs text-slate-400 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
              <div className="flex justify-between">
                <span>Avg Focus Score:</span>
                <strong className="text-emerald-400">{d.focus}</strong>
              </div>
              <div className="flex justify-between">
                <span>Avg Burnout Risk:</span>
                <strong className="text-rose-400">{d.burnout}%</strong>
              </div>
              <div className="flex justify-between">
                <span>Avg Department CGPA:</span>
                <strong className="text-purple-400">{d.cgpa}</strong>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
