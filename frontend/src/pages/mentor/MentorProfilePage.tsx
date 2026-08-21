import React from 'react';
import { Award, Mail, Building } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const MentorProfilePage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Mentor Profile</h1>
        <p className="text-xs text-slate-400 mt-1">Faculty profile and academic designation</p>
      </div>

      <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-2xl shadow-lg shadow-indigo-500/20">
            {user?.name?.charAt(0) || 'M'}
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">{user?.name || 'Dr. Robert Vance'}</h2>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 inline-block mt-1">
              Associate Professor & Senior Mentor
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl glass-panel border border-slate-800">
            <p className="text-xs text-slate-400">Department</p>
            <p className="text-sm font-semibold text-white mt-1">{user?.department || 'Computer Science'}</p>
          </div>

          <div className="p-4 rounded-xl glass-panel border border-slate-800">
            <p className="text-xs text-slate-400">Email Address</p>
            <p className="text-sm font-semibold text-white mt-1">{user?.email || 'vance@studiq.edu'}</p>
          </div>
        </div>
      </div>
    </div>
  );
};
