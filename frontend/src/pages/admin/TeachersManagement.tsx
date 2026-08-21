import React, { useState } from 'react';
import { UserCheck, Search, Plus, Edit3, Key } from 'lucide-react';
import { Badge } from '../../components/Badge';
import { useToast } from '../../context/ToastContext';

export const TeachersManagement: React.FC = () => {
  const { showToast } = useToast();
  const [searchTerm, setSearchTerm] = useState('');

  const teachers = [
    { id: 1, teacher_id: 'TCH-2026-001', name: 'Prof. Robert Vance', email: 'prof.vance@studiq.edu', department: 'Computer Science', course: 'Machine Learning' },
    { id: 2, teacher_id: 'TCH-2026-002', name: 'Prof. Elena Rostova', email: 'prof.rostova@studiq.edu', department: 'Electronics & Comm', course: 'Signals & Systems' },
    { id: 3, teacher_id: 'TCH-2026-003', name: 'Prof. Marcus Brody', email: 'prof.brody@studiq.edu', department: 'Mechanical Eng', course: 'Thermodynamics' }
  ];

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <UserCheck className="w-6 h-6 text-emerald-400" />
            Teachers Directory & Course Instructors
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Manage course instructors across 5 departments and course assignments.
          </p>
        </div>

        <button
          onClick={() => showToast('Enroll Teacher modal ready', 'info')}
          className="bg-brand-600 text-white font-semibold text-xs py-2.5 px-4 rounded-xl flex items-center gap-2"
        >
          <Plus className="w-4 h-4" /> Add New Teacher
        </button>
      </div>

      <div className="glass-card rounded-2xl p-6 border border-slate-800">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 text-slate-400 font-semibold uppercase font-mono">
              <tr>
                <th className="py-3 px-4">Teacher ID</th>
                <th className="py-3 px-4">Name</th>
                <th className="py-3 px-4">Email</th>
                <th className="py-3 px-4">Department</th>
                <th className="py-3 px-4">Course</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {teachers.map((t) => (
                <tr key={t.id} className="hover:bg-slate-900/40 transition">
                  <td className="py-3.5 px-4 font-mono text-emerald-400 font-semibold">{t.teacher_id}</td>
                  <td className="py-3.5 px-4 font-semibold text-slate-100">{t.name}</td>
                  <td className="py-3.5 px-4 text-slate-400">{t.email}</td>
                  <td className="py-3.5 px-4">{t.department}</td>
                  <td className="py-3.5 px-4 font-semibold text-brand-400">{t.course}</td>
                  <td className="py-3.5 px-4 text-right space-x-1">
                    <button onClick={() => showToast(`Edit ${t.name}`, 'info')} className="p-1.5 rounded-lg bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800">
                      <Edit3 className="w-3.5 h-3.5" />
                    </button>
                    <button onClick={() => showToast(`Reset pass for ${t.name}`, 'info')} className="p-1.5 rounded-lg bg-slate-900 text-purple-400 hover:text-purple-300 border border-slate-800">
                      <Key className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
