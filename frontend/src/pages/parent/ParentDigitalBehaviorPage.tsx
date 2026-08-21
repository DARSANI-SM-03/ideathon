import React, { useEffect, useState } from 'react';
import { Monitor, Clock, ShieldAlert, Cpu, CheckCircle } from 'lucide-react';
import { ParentService } from '../../services/parentService';
import { DigitalBehavior } from '../../types';

export const ParentDigitalBehaviorPage: React.FC = () => {
  const [data, setData] = useState<DigitalBehavior | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    ParentService.getDigitalBehavior().then(res => {
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
        <h1 className="text-2xl font-bold text-white tracking-tight">Digital Behavior & Screentime Analytics</h1>
        <p className="text-xs text-slate-400 mt-1">Real-time desktop application telemetry and category breakdown</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <div className="glass-card p-6 rounded-2xl border border-slate-800">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Monitor className="w-5 h-5 text-cyan-400" /> Screentime Allocation (Today)
          </h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-300">Productive & Coding</span>
                <span className="font-bold text-white">{data.today.productive} mins</span>
              </div>
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-brand-500 rounded-full" style={{ width: '70%' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-300">Educational Video & Lectures</span>
                <span className="font-bold text-white">{data.today.educational} mins</span>
              </div>
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-cyan-400 rounded-full" style={{ width: '45%' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-300">Entertainment & Streaming</span>
                <span className="font-bold text-white">{data.today.entertainment} mins</span>
              </div>
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-amber-400 rounded-full" style={{ width: '25%' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-300">Gaming</span>
                <span className="font-bold text-white">{data.today.gaming} mins</span>
              </div>
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-rose-500 rounded-full" style={{ width: '15%' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Top Applications */}
        <div className="glass-card p-6 rounded-2xl border border-slate-800">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-indigo-400" /> Active Application Telemetry
          </h2>
          <div className="space-y-3">
            {data.topApps.map((app) => (
              <div key={app.appName} className="flex items-center justify-between p-3.5 rounded-xl glass-panel border border-slate-800/80">
                <div className="flex items-center gap-3">
                  <span className="text-xl">{app.iconEmoji}</span>
                  <div>
                    <p className="text-xs font-bold text-white">{app.appName}</p>
                    <span className="text-[10px] text-slate-400">{app.category}</span>
                  </div>
                </div>
                <span className="text-xs font-mono font-bold text-brand-400">{app.timeMinutes} mins</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
