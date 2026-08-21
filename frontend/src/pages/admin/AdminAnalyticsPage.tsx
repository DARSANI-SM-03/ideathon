import React from 'react';
import { FocusVsBurnoutScatter } from '../../charts/FocusVsBurnoutScatter';
import { DepartmentComparisonChart } from '../../charts/DepartmentComparisonChart';
import { BarChart3, TrendingUp, ShieldAlert, Award } from 'lucide-react';

export const AdminAnalyticsPage: React.FC = () => {
  const departments = [
    { department: 'Computer Science', student_count: 55, avg_focus_score: 82.4, avg_burnout_score: 28.1, avg_cgpa: 3.52 },
    { department: 'Electronics & Comm', student_count: 42, avg_focus_score: 76.5, avg_burnout_score: 34.2, avg_cgpa: 3.38 },
    { department: 'Mechanical Eng', student_count: 38, avg_focus_score: 75.1, avg_burnout_score: 33.8, avg_cgpa: 3.29 },
    { department: 'Electrical Eng', student_count: 35, avg_focus_score: 79.0, avg_burnout_score: 29.5, avg_cgpa: 3.44 },
    { department: 'Civil Eng', student_count: 30, avg_focus_score: 74.8, avg_burnout_score: 35.6, avg_cgpa: 3.25 }
  ];

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-brand-400" />
          Institutional Predictive Analytics Deep Dive
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Cluster analysis and burnout predictive modeling across institutional demographics.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-400" />
            Focus vs Burnout Scatter Distribution
          </h3>
          <FocusVsBurnoutScatter />
        </div>

        <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
            <Award className="w-5 h-5 text-purple-400" />
            Department Performance Analytics
          </h3>
          <DepartmentComparisonChart data={departments} />
        </div>
      </div>
    </div>
  );
};
