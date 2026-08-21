import React, { useEffect, useState } from 'react';
import { ApiService } from '../../services/api';
import { AdminDashboardData } from '../../types';
import { StatCard } from '../../components/StatCard';
import { Modal } from '../../components/Modal';
import { DepartmentComparisonChart } from '../../charts/DepartmentComparisonChart';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  UserCheck,
  Award,
  HeartHandshake,
  Brain,
  Flame,
  ShieldAlert,
  Radio,
  Building,
  ArrowRight,
  FileText,
  Sliders,
  Activity,
  UserPlus,
  CheckCircle2
} from 'lucide-react';

export const AdminDashboard: React.FC = () => {
  const [data, setData] = useState<AdminDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState('Alex Mercer (STU-2026-001)');
  const [selectedMentor, setSelectedMentor] = useState('Dr. Robert Vance');
  const [assignSuccess, setAssignSuccess] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    ApiService.fetchAdminDashboard().then((res) => {
      setData(res);
      setLoading(false);
    });
  }, []);

  if (loading || !data) {
    return (
      <div className="p-12 text-center text-slate-400 font-sans">
        <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        Loading Institutional Intelligence Console...
      </div>
    );
  }

  const handleAssignMentor = async (e: React.FormEvent) => {
    e.preventDefault();
    await ApiService.assignMentor(selectedStudent, selectedMentor);
    setAssignSuccess(true);
    setTimeout(() => {
      setAssignSuccess(false);
      setAssignModalOpen(false);
      ApiService.fetchAdminDashboard().then((res) => setData(res));
    }, 1200);
  };

  return (
    <div className="space-y-6 pb-12 font-sans">
      {/* Executive Header Banner */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-white">Institutional Executive Console</h1>
            <span className="px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20 text-xs font-mono font-bold">
              Campus Oversight Active
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Institutional overview across {data.institution_analytics.total_departments || data.department_analytics.length} Departments and {data.total_students} Enrolled Students.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setAssignModalOpen(true)}
            className="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold flex items-center gap-2 transition shadow-lg shadow-brand-500/20"
          >
            <UserPlus className="w-4 h-4" /> Assign Mentor to Student
          </button>
        </div>
      </div>

      {/* INSTITUTION OVERVIEW METRICS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Students" value={`${data.total_students} Enrolled`} subtitle="Active Telemetry Database" icon={Users} variant="blue" />
        <StatCard title="Campus Attendance" value={`${data.institution_analytics.overall_attendance_avg}%`} subtitle="Institutional Average" icon={Award} variant="purple" />
        <StatCard title="Campus CGPA" value={`${data.institution_analytics.overall_cgpa_avg}`} subtitle="Academic Performance" icon={HeartHandshake} variant="emerald" />
        <StatCard title="Total Departments" value={`${data.institution_analytics.total_departments || data.department_analytics.length} Active`} subtitle="Academic Staff Oversight" icon={UserCheck} variant="amber" />
      </div>

      {/* SYSTEM HEALTH & AI GAUGES */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard title="Campus Focus Average" value={`${data.avg_focus_score}`} subtitle="Target >75.0 Index" icon={Brain} variant="emerald" />
        <StatCard title="Campus Burnout Baseline" value={`${data.avg_burnout_score}%`} subtitle="Institutional Baseline" icon={Flame} variant="amber" />
        <StatCard title="High Risk Students" value={`${data.high_risk_students_count}`} subtitle="Action Queue Priority" icon={ShieldAlert} variant="rose" />
      </div>

      {/* CORE MANAGEMENT DIRECTORY SHORTS */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Building className="w-5 h-5 text-brand-400" /> Core Administrative Directories
          </h3>
          <span className="text-xs font-mono text-slate-400">Institutional Governance</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <button
            onClick={() => navigate('/admin/students')}
            className="p-4 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-left transition group"
          >
            <Users className="w-5 h-5 text-brand-400 mb-2 group-hover:scale-110 transition" />
            <div className="text-xs font-bold text-white">Students Management</div>
            <p className="text-[11px] text-slate-400 mt-0.5">{data.total_students} Student Records</p>
          </button>

          <button
            onClick={() => navigate('/admin/parents')}
            className="p-4 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-left transition group"
          >
            <HeartHandshake className="w-5 h-5 text-emerald-400 mb-2 group-hover:scale-110 transition" />
            <div className="text-xs font-bold text-white">Parents Directory</div>
            <p className="text-[11px] text-slate-400 mt-0.5">Consent & Notifications</p>
          </button>

          <button
            onClick={() => navigate('/admin/mentors')}
            className="p-4 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-left transition group"
          >
            <Award className="w-5 h-5 text-purple-400 mb-2 group-hover:scale-110 transition" />
            <div className="text-xs font-bold text-white">Mentors Allocation</div>
            <p className="text-[11px] text-slate-400 mt-0.5">Faculty Workloads</p>
          </button>

          <button
            onClick={() => navigate('/admin/teachers')}
            className="p-4 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-left transition group"
          >
            <UserCheck className="w-5 h-5 text-amber-400 mb-2 group-hover:scale-110 transition" />
            <div className="text-xs font-bold text-white">Teachers & Faculty</div>
            <p className="text-[11px] text-slate-400 mt-0.5">Course Assignments</p>
          </button>
        </div>
      </div>


      {/* DEPARTMENT ANALYTICS & REPORTS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
            <Building className="w-5 h-5 text-emerald-400" />
            Department Focus & Burnout Comparison
          </h3>
          <DepartmentComparisonChart data={data.department_analytics} />
        </div>

        <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Sliders className="w-5 h-5 text-purple-400" /> AI Settings & System Health
              </h3>
              <span className="text-xs font-mono text-emerald-400">All Engines Operational</span>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                <span className="text-slate-300 font-semibold">Burnout Predictor Model</span>
                <span className="font-mono text-emerald-400">v2.4 (High Precision)</span>
              </div>

              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                <span className="text-slate-300 font-semibold">Telemetry Ingestion Rate</span>
                <span className="font-mono text-brand-400">10s Buffer Stream</span>
              </div>

              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                <span className="text-slate-300 font-semibold">Parent Consent Policy</span>
                <span className="font-mono text-purple-400">Strict OTP Mandatory</span>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
            <button
              onClick={() => navigate('/admin/reports')}
              className="text-xs font-bold text-brand-400 hover:underline flex items-center gap-1.5"
            >
              <FileText className="w-4 h-4" /> Export Campus Intelligence Report
            </button>
            <span className="text-[10px] font-mono text-slate-500">StudIQ Core v1.0</span>
          </div>
        </div>
      </div>

      {/* Assign Mentor Modal */}
      <Modal
        isOpen={assignModalOpen}
        onClose={() => setAssignModalOpen(false)}
        title="Assign Faculty Mentor to Student"
      >
        {assignSuccess ? (
          <div className="py-6 text-center space-y-2">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
            <h4 className="text-base font-bold text-white">Mentor Assigned Successfully!</h4>
            <p className="text-xs text-slate-400">Allocation logged and notification sent to student & parent.</p>
          </div>
        ) : (
          <form onSubmit={handleAssignMentor} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Select Student</label>
              <select
                value={selectedStudent}
                onChange={(e) => setSelectedStudent(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none"
              >
                <option value="Alex Mercer (STU-2026-001)">Alex Mercer (STU-2026-001) - High Risk</option>
                <option value="Jordan Hayes (STU-2026-042)">Jordan Hayes (STU-2026-042) - Medium Risk</option>
                <option value="Taylor Swift (STU-2026-088)">Taylor Swift (STU-2026-088) - High Risk</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Assign Faculty Mentor</label>
              <select
                value={selectedMentor}
                onChange={(e) => setSelectedMentor(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none"
              >
                <option value="Dr. Robert Vance">Dr. Robert Vance (CS Department)</option>
                <option value="Prof. Sarah Jenkins">Prof. Sarah Jenkins (ECE Department)</option>
                <option value="Dr. Michael Chang">Dr. Michael Chang (Data Science)</option>
              </select>
            </div>

            <button
              type="submit"
              className="w-full bg-brand-600 hover:bg-brand-500 text-white font-bold py-2.5 rounded-xl text-xs shadow-lg transition"
            >
              Confirm Mentor Allocation
            </button>
          </form>
        )}
      </Modal>
    </div>
  );
};
