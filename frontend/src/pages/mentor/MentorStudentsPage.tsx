import React, { useEffect, useState } from 'react';
import { Users, Search, Filter, ShieldAlert, GraduationCap } from 'lucide-react';
import { MentorService } from '../../services/mentorService';
import { MentorStudent } from '../../types';

export const MentorStudentsPage: React.FC = () => {
  const [students, setStudents] = useState<MentorStudent[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    MentorService.getAssignedStudents().then(res => {
      setStudents(res);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const filtered = students.filter(s => s.name.toLowerCase().includes(search.toLowerCase()) || s.studentId.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Assigned Mentees</h1>
          <p className="text-xs text-slate-400 mt-1">Directory of students under your mentorship cohort</p>
        </div>

        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search mentees by name or ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 w-64"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {filtered.map((s) => (
          <div key={s.id} className="glass-card p-5 rounded-2xl border border-slate-800 flex flex-col justify-between space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-base shadow-lg shadow-indigo-500/20">
                {s.name.charAt(0)}
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">{s.name}</h3>
                <p className="text-[11px] text-slate-400 font-mono">{s.studentId} &bull; Sem {s.semester}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2 rounded-lg bg-slate-900/60 border border-slate-800/80">
                <span className="text-slate-500 text-[10px] uppercase block">Focus Score</span>
                <span className="font-bold text-emerald-400 text-sm">{s.focusScore}</span>
              </div>
              <div className="p-2 rounded-lg bg-slate-900/60 border border-slate-800/80">
                <span className="text-slate-500 text-[10px] uppercase block">Burnout Risk</span>
                <span className={`font-bold text-sm uppercase ${s.burnoutRisk === 'critical' || s.burnoutRisk === 'high' ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {s.burnoutRisk}
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-xs">
              <span className="text-slate-400">Attendance: <strong className="text-white">{s.attendance}%</strong></span>
              <span className="text-slate-400">CGPA: <strong className="text-brand-400">{s.cgpa}</strong></span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
