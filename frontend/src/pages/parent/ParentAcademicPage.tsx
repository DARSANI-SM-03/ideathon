import React, { useEffect, useState } from 'react';
import { GraduationCap, BookOpen, Award, CheckCircle2, TrendingUp, UserCheck } from 'lucide-react';
import { ParentService } from '../../services/parentService';
import { AcademicOverview } from '../../types';

export const ParentAcademicPage: React.FC = () => {
  const [data, setData] = useState<AcademicOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    ParentService.getAcademicOverview().then(res => {
      setData(res);
      setLoading(false);
    });
  }, []);

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Academic Performance Overview</h1>
        <p className="text-xs text-slate-400 mt-1">Detailed subject performance, attendance tracking, and faculty evaluations</p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <p className="text-xs font-semibold text-slate-400 uppercase">Overall CGPA</p>
          <p className="text-3xl font-extrabold text-white mt-1">{data.cgpa}</p>
          <span className="text-[11px] text-emerald-400">Consistent Top Tier</span>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <p className="text-xs font-semibold text-slate-400 uppercase">Overall Attendance</p>
          <p className="text-3xl font-extrabold text-emerald-400 mt-1">{data.attendancePercent}%</p>
          <span className="text-[11px] text-slate-400">Target: &ge; 75%</span>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <p className="text-xs font-semibold text-slate-400 uppercase">Assignments</p>
          <p className="text-3xl font-extrabold text-indigo-400 mt-1">{data.assignmentsCompleted} / {data.assignmentsTotal}</p>
          <span className="text-[11px] text-indigo-300">{data.assignmentsPending} Pending Submission</span>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <p className="text-xs font-semibold text-slate-400 uppercase">Quiz Average</p>
          <p className="text-3xl font-extrabold text-cyan-400 mt-1">{data.quizAverage}%</p>
          <span className="text-[11px] text-cyan-300">Continuous Assessment</span>
        </div>
      </div>

      {/* Subject Wise Performance */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800">
        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-brand-400" /> Enrolled Subjects & Grades
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase font-mono">
                <th className="py-3 px-4">Subject</th>
                <th className="py-3 px-4">Code</th>
                <th className="py-3 px-4">Attendance</th>
                <th className="py-3 px-4">Grade</th>
                <th className="py-3 px-4">Marks</th>
                <th className="py-3 px-4">Quiz Avg</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs">
              {data.subjects.map((sub) => (
                <tr key={sub.code} className="hover:bg-slate-900/50 transition">
                  <td className="py-3.5 px-4 font-semibold text-white">{sub.subject}</td>
                  <td className="py-3.5 px-4 font-mono text-slate-400">{sub.code}</td>
                  <td className="py-3.5 px-4 font-bold text-emerald-400">{sub.attendance}%</td>
                  <td className="py-3.5 px-4">
                    <span className="px-2.5 py-1 rounded-lg bg-brand-500/15 text-brand-400 border border-brand-500/30 font-bold font-mono">
                      {sub.grade}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-200">{sub.marks} / {sub.maxMarks}</td>
                  <td className="py-3.5 px-4 text-cyan-400 font-semibold">{sub.quizAvg}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Faculty Feedback */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800">
        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <UserCheck className="w-5 h-5 text-emerald-400" /> Faculty Evaluations & Feedback
        </h2>
        <div className="space-y-4">
          {data.teacherFeedback.map((fb) => (
            <div key={fb.id} className="glass-panel p-4 rounded-xl border border-slate-800/80">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold text-white">{fb.teacher} <span className="text-slate-500 font-normal">({fb.subject})</span></p>
                  <p className="text-xs text-slate-300 mt-1">{fb.message}</p>
                </div>
                <span className="text-[10px] text-slate-500 font-mono">{fb.date}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
