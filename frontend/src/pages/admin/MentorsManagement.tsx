import React from 'react';
import { Award, Plus, Edit3, Key } from 'lucide-react';
import { useToast } from '../../context/ToastContext';

export const MentorsManagement: React.FC = () => {
  const { showToast } = useToast();

  const mentors = [
    { id: 1, mentor_id: 'MNT-2026-001', name: 'Dr. Arthur Pendelton', email: 'mentor.arthur@studiq.edu', department: 'Computer Science', capacity: 15, assigned: 12 },
    { id: 2, mentor_id: 'MNT-2026-002', name: 'Dr. Samantha Reed', email: 'mentor.reed@studiq.edu', department: 'Electronics & Comm', capacity: 15, assigned: 15 },
  ];

  return (
    <div className="space-y-6 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Award className="w-6 h-6 text-purple-400" />
            Mentors Management Roster
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Manage academic mentors, capacity allocations, and student intervention assignments.
          </p>
        </div>

        <button onClick={() => showToast('Add Mentor trigger ready', 'info')} className="bg-brand-600 text-white font-semibold text-xs py-2.5 px-4 rounded-xl flex items-center gap-2">
          <Plus className="w-4 h-4" /> Add Academic Mentor
        </button>
      </div>

      <div className="glass-card rounded-2xl p-6 border border-slate-800">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 text-slate-400 font-semibold uppercase font-mono">
              <tr>
                <th className="py-3 px-4">Mentor ID</th>
                <th className="py-3 px-4">Name</th>
                <th className="py-3 px-4">Email</th>
                <th className="py-3 px-4">Department</th>
                <th className="py-3 px-4">Capacity</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {mentors.map((m) => (
                <tr key={m.id} className="hover:bg-slate-900/40 transition">
                  <td className="py-3.5 px-4 font-mono text-purple-400 font-semibold">{m.mentor_id}</td>
                  <td className="py-3.5 px-4 font-semibold text-slate-100">{m.name}</td>
                  <td className="py-3.5 px-4 text-slate-400">{m.email}</td>
                  <td className="py-3.5 px-4">{m.department}</td>
                  <td className="py-3.5 px-4 font-mono">{m.assigned} / {m.capacity} Mentees</td>
                  <td className="py-3.5 px-4 text-right space-x-1">
                    <button onClick={() => showToast(`Edit ${m.name}`, 'info')} className="p-1.5 rounded-lg bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800">
                      <Edit3 className="w-3.5 h-3.5" />
                    </button>
                    <button onClick={() => showToast(`Reset pass for ${m.name}`, 'info')} className="p-1.5 rounded-lg bg-slate-900 text-purple-400 border border-slate-800">
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
