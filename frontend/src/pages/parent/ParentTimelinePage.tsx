import React, { useEffect, useState } from 'react';
import { History, Clock, BookOpen, Monitor } from 'lucide-react';
import { ParentService } from '../../services/parentService';
import { TimelineActivity } from '../../types';

export const ParentTimelinePage: React.FC = () => {
  const [activities, setActivities] = useState<TimelineActivity[]>([]);

  useEffect(() => {
    ParentService.getTimelineActivities().then(setActivities);
  }, []);

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Activity Timeline</h1>
        <p className="text-xs text-slate-400 mt-1">Sequential log of academic work, study sessions, and breaks</p>
      </div>

      <div className="glass-card p-6 rounded-2xl border border-slate-800">
        <div className="relative border-l-2 border-slate-800 ml-4 space-y-6">
          {activities.map((act) => (
            <div key={act.id} className="relative pl-6">
              <div className="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-brand-500 border-2 border-slate-950" />
              <div className="glass-panel p-4 rounded-xl border border-slate-800/80">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-brand-400">{act.time}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">{act.category}</span>
                </div>
                <h3 className="text-xs font-bold text-white mt-1">{act.appName}</h3>
                {act.note && <p className="text-xs text-slate-400 mt-1">{act.note}</p>}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
