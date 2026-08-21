import React from 'react';
import { HeartHandshake, Plus, Edit3, Key } from 'lucide-react';
import { useToast } from '../../context/ToastContext';

export const ParentsManagement: React.FC = () => {
  const { showToast } = useToast();

  const parents = [
    { id: 1, parent_id: 'PAR-2026-001', name: 'Eleanor Mercer', email: 'parent.mercer@gmail.com', student_name: 'Alex Mercer (STU-2026-001)', phone: '+1-555-0101' },
    { id: 2, parent_id: 'PAR-2026-002', name: 'Charles Smith', email: 'parent.smith@gmail.com', student_name: 'Sophia Smith (STU-2026-002)', phone: '+1-555-0102' },
  ];

  return (
    <div className="space-y-6 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <HeartHandshake className="w-6 h-6 text-brand-400" />
            Parents Portal Directory
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Registered parent accounts linked with student IDs for automated burnout escalation alerts.
          </p>
        </div>

        <button onClick={() => showToast('Register Parent modal ready', 'info')} className="bg-brand-600 text-white font-semibold text-xs py-2.5 px-4 rounded-xl flex items-center gap-2">
          <Plus className="w-4 h-4" /> Link New Parent Account
        </button>
      </div>

      <div className="glass-card rounded-2xl p-6 border border-slate-800">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 text-slate-400 font-semibold uppercase font-mono">
              <tr>
                <th className="py-3 px-4">Parent ID</th>
                <th className="py-3 px-4">Parent Name</th>
                <th className="py-3 px-4">Email</th>
                <th className="py-3 px-4">Linked Student</th>
                <th className="py-3 px-4">Phone</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {parents.map((p) => (
                <tr key={p.id} className="hover:bg-slate-900/40 transition">
                  <td className="py-3.5 px-4 font-mono text-brand-400 font-semibold">{p.parent_id}</td>
                  <td className="py-3.5 px-4 font-semibold text-slate-100">{p.name}</td>
                  <td className="py-3.5 px-4 text-slate-400">{p.email}</td>
                  <td className="py-3.5 px-4 font-semibold text-emerald-400">{p.student_name}</td>
                  <td className="py-3.5 px-4 font-mono">{p.phone}</td>
                  <td className="py-3.5 px-4 text-right space-x-1">
                    <button onClick={() => showToast(`Edit ${p.name}`, 'info')} className="p-1.5 rounded-lg bg-slate-900 text-slate-400 border border-slate-800">
                      <Edit3 className="w-3.5 h-3.5" />
                    </button>
                    <button onClick={() => showToast(`Reset pass for ${p.name}`, 'info')} className="p-1.5 rounded-lg bg-slate-900 text-purple-400 border border-slate-800">
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
