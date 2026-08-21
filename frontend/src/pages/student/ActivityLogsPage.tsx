import React, { useEffect, useState } from 'react';
import { ApiService } from '../../services/api';
import { ActivityLog } from '../../types';
import { Badge } from '../../components/Badge';
import { Activity, Radio, Plus, Check } from 'lucide-react';

export const ActivityLogsPage: React.FC = () => {
  const [activities, setActivities] = useState<ActivityLog[]>([]);
  const [testApp, setTestApp] = useState('VS Code');
  const [testTitle, setTestTitle] = useState('main.py - StudIQ AI Engine');
  const [testDuration, setTestDuration] = useState(15);
  const [ingestStatus, setIngestStatus] = useState<string | null>(null);

  useEffect(() => {
    ApiService.fetchStudentActivities().then(setActivities);
  }, []);

  const handleTestTelemetry = async (e: React.FormEvent) => {
    e.preventDefault();
    setIngestStatus('Processing telemetry...');
    const result = await ApiService.sendTelemetry({
      student_id: 1,
      application_name: testApp,
      window_title: testTitle,
      duration: testDuration * 60
    });
    setIngestStatus(`Telemetry Logged! Category: ${result.assigned_category || 'Coding'}`);
    setTimeout(() => setIngestStatus(null), 4000);
  };

  return (
    <div className="space-y-6 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Activity className="w-6 h-6 text-brand-400" />
            Digital Activity & App Usage Logs
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time classification of background desktop applications and web browsing sessions.
          </p>
        </div>
      </div>

      {/* Telemetry Simulator Box */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800">
        <h3 className="text-base font-bold text-slate-100 mb-2 flex items-center gap-2">
          <Radio className="w-4 h-4 text-emerald-400" />
          Test Monitoring Telemetry Ingestion API
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Simulate a desktop telemetry ping sent by the StudIQ background agent.
        </p>

        <form onSubmit={handleTestTelemetry} className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <input
            type="text"
            value={testApp}
            onChange={(e) => setTestApp(e.target.value)}
            placeholder="Application Name"
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200"
          />
          <input
            type="text"
            value={testTitle}
            onChange={(e) => setTestTitle(e.target.value)}
            placeholder="Window Title"
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200"
          />
          <input
            type="number"
            value={testDuration}
            onChange={(e) => setTestDuration(Number(e.target.value))}
            placeholder="Duration (mins)"
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200"
          />
          <button
            type="submit"
            className="bg-brand-600 hover:bg-brand-500 text-white font-medium text-xs rounded-xl py-2 px-4 flex items-center justify-center gap-1.5 transition"
          >
            <Plus className="w-4 h-4" /> Send Telemetry Ping
          </button>
        </form>

        {ingestStatus && (
          <div className="mt-3 text-xs font-mono text-emerald-400 bg-emerald-500/10 p-2 rounded.xl border border-emerald-500/20 flex items-center gap-2">
            <Check className="w-4 h-4" /> {ingestStatus}
          </div>
        )}
      </div>

      {/* Activities Timeline Table */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800">
        <h3 className="text-base font-bold text-slate-100 mb-4">Recent Ingested Activity Feed</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 text-slate-400 font-semibold uppercase font-mono">
              <tr>
                <th className="py-3 px-4">Application</th>
                <th className="py-3 px-4">Window Title / Context</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Duration</th>
                <th className="py-3 px-4">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {activities.map((act) => (
                <tr key={act.activity_id} className="hover:bg-slate-900/40 transition">
                  <td className="py-3 px-4 font-semibold text-slate-200">{act.application_name}</td>
                  <td className="py-3 px-4 truncate max-w-xs text-slate-400">{act.window_title || 'N/A'}</td>
                  <td className="py-3 px-4">
                    <Badge variant={act.category === 'Entertainment' || act.category === 'Gaming' ? 'high' : 'info'}>
                      {act.category}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 font-mono">{Math.round(act.duration / 60)} mins</td>
                  <td className="py-3 px-4 text-slate-500 font-mono">{act.start_time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
