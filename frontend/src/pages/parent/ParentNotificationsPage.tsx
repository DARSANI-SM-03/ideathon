import React from 'react';
import { Bell, AlertTriangle, Info, CheckCircle2 } from 'lucide-react';

export const ParentNotificationsPage: React.FC = () => {
  const notifications = [
    { id: '1', title: 'Focus Score Alert', message: 'Alex achieved a peak focus score of 94 during morning lab session.', type: 'info', time: '2 hours ago' },
    { id: '2', title: 'Weekly Behavioral Report Ready', message: 'The AI weekly digest for July Week 4 has been generated.', type: 'success', time: '1 day ago' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Parent Notifications & Alerts</h1>
        <p className="text-xs text-slate-400 mt-1">Real-time alerts regarding academic updates, screentime caps, and AI insights</p>
      </div>

      <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-3">
        {notifications.map((n) => (
          <div key={n.id} className="p-4 rounded-xl glass-panel border border-slate-800 flex items-start gap-3">
            <Bell className="w-5 h-5 text-brand-400 mt-0.5" />
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold text-white">{n.title}</h3>
                <span className="text-[10px] text-slate-500 font-mono">{n.time}</span>
              </div>
              <p className="text-xs text-slate-300 mt-1">{n.message}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
