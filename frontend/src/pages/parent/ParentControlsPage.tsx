import React, { useEffect, useState } from 'react';
import { Shield, Clock, Lock, CheckCircle2, Sliders } from 'lucide-react';
import { ParentService } from '../../services/parentService';
import { ParentControls } from '../../types';

export const ParentControlsPage: React.FC = () => {
  const [controls, setControls] = useState<ParentControls | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    ParentService.getControls().then(res => {
      setControls(res);
      setLoading(false);
    });
  }, []);

  if (loading || !controls) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Parental Guidance & Digital Boundaries</h1>
        <p className="text-xs text-slate-400 mt-1">Manage entertainment caps, application permissions, and quiet hours</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Time Limits */}
        <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Clock className="w-5 h-5 text-amber-400" /> Daily Screentime Limits
          </h2>
          <div>
            <label className="text-xs font-semibold text-slate-300">Weekday Entertainment Cap</label>
            <div className="flex items-center justify-between mt-1 p-3 rounded-xl glass-panel border border-slate-800">
              <span className="text-sm font-bold text-white">{controls.dailyEntertainmentLimitMinutes} Minutes / Day</span>
              <span className="text-[10px] text-emerald-400 font-mono font-bold">Active</span>
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300">Weekend Entertainment Cap</label>
            <div className="flex items-center justify-between mt-1 p-3 rounded-xl glass-panel border border-slate-800">
              <span className="text-sm font-bold text-white">{controls.weekendEntertainmentLimitMinutes} Minutes / Day</span>
              <span className="text-[10px] text-emerald-400 font-mono font-bold">Active</span>
            </div>
          </div>
        </div>

        {/* Schedule */}
        <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Shield className="w-5 h-5 text-emerald-400" /> Core Study Window
          </h2>
          <div>
            <label className="text-xs font-semibold text-slate-300">Focus Hours Window</label>
            <div className="p-3 rounded-xl glass-panel border border-slate-800 flex items-center justify-between font-mono text-sm text-brand-400">
              <span>{controls.studyScheduleStart} AM</span>
              <span>&rarr;</span>
              <span>{controls.studyScheduleEnd} PM</span>
            </div>
          </div>
          <p className="text-[11px] text-slate-400">Non-academic applications are automatically throttled during focus windows.</p>
        </div>
      </div>
    </div>
  );
};
