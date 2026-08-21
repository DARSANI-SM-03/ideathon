import React, { useEffect, useState } from 'react';
import { ApiService } from '../../services/api';
import { LiveActivity } from '../../types';
import { Badge } from '../../components/Badge';
import { Radio, Play, Pause, Activity } from 'lucide-react';

export const LiveMonitoringPage: React.FC = () => {
  const [feed, setFeed] = useState<LiveActivity[]>([]);
  const [isStreaming, setIsStreaming] = useState(true);

  useEffect(() => {
    const fetchTelemetry = () => {
      ApiService.fetchAdminDashboard().then((res) => {
        if (res && res.live_monitoring_summary && res.live_monitoring_summary.recent_activities) {
          setFeed(res.live_monitoring_summary.recent_activities);
        }
      });
    };

    fetchTelemetry();

    const interval = setInterval(() => {
      if (isStreaming) {
        fetchTelemetry();
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [isStreaming]);


  return (
    <div className="space-y-6 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Radio className="w-6 h-6 text-emerald-400 animate-pulse" />
            Live App & Web Usage Telemetry Stream
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time background monitoring ingestion stream capturing application windows and categorization.
          </p>
        </div>

        <button
          onClick={() => setIsStreaming(!isStreaming)}
          className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition ${
            isStreaming
              ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
              : 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
          }`}
        >
          {isStreaming ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          {isStreaming ? 'Pause Real-time Feed' : 'Resume Real-time Feed'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {feed.map((act) => (
          <div
            key={act.activity_id}
            className="glass-card p-4 rounded-2xl border border-slate-800 transition hover:border-slate-700 animate-in fade-in duration-300"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Activity className="w-4 h-4 text-brand-400" />
                {act.application_name}
              </span>
              <Badge variant={act.category === 'Entertainment' || act.category === 'Social Media' ? 'high' : 'info'}>
                {act.category}
              </Badge>
            </div>
            <p className="text-xs text-slate-400 truncate mb-3">{act.window_title || 'Active Application Session'}</p>
            <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-500">
              <span>Student ID #{act.student_id}</span>
              <span>{act.duration_mins} mins</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
