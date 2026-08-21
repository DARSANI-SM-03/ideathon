import React from 'react';
import { Bell, ShieldAlert } from 'lucide-react';

export const MentorNotificationsPage: React.FC = () => {
  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Mentor Alerts & Notifications</h1>
        <p className="text-xs text-slate-400 mt-1">High burnout risk alerts and counseling reminders</p>
      </div>

      <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-3">
        <div className="p-4 rounded-xl glass-panel border border-slate-800 flex items-start gap-3">
          <ShieldAlert className="w-5 h-5 text-rose-400 mt-0.5" />
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-white">Critical Burnout Spike: Marcus Chen</h3>
              <span className="text-[10px] text-slate-500 font-mono">1 hour ago</span>
            </div>
            <p className="text-xs text-slate-300 mt-1">Marcus Chen's burnout score reached 88/100 following late-night gaming. Priority queue updated.</p>
          </div>
        </div>
      </div>
    </div>
  );
};
