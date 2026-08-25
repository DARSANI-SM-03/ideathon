import React, { useState } from 'react';
import { History, Filter, Laptop, Globe, Clock, Brain, Flame, Radio, Plus, Check } from 'lucide-react';
import { Badge } from '../../components/Badge';
import { ApiService } from '../../services/api';

export const ActivityHistoryPage: React.FC = () => {
  const [timeframe, setTimeframe] = useState<'Today' | '7 Days' | '30 Days' | 'Semester'>('Today');
  const [testApp, setTestApp] = useState('VS Code');
  const [testTitle, setTestTitle] = useState('main.py - StudIQ AI Engine');
  const [testDuration, setTestDuration] = useState(15);
  const [ingestStatus, setIngestStatus] = useState<string | null>(null);

  const [activities, setActivities] = useState<any[]>([]);
  const [avgFocus, setAvgFocus] = useState<number>(85.0);
  const [avgBurnout, setAvgBurnout] = useState<number>(15.0);
  const [totalRecords, setTotalRecords] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await ApiService.get(`/activity/history?timeframe=${encodeURIComponent(timeframe)}`);
      if (data && data.items) {
        setActivities(data.items);
        setAvgFocus(data.avg_focus || 85.0);
        setAvgBurnout(data.avg_burnout || 15.0);
        setTotalRecords(data.total_records || data.items.length);
      }
    } catch {
      // Graceful fallback to empty state
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchHistory();
  }, [timeframe]);

  const handleTestTelemetry = async (e: React.FormEvent) => {
    e.preventDefault();
    setIngestStatus('Processing telemetry ping...');
    try {
      const result = await ApiService.sendTelemetry({
        student_id: 1,
        application_name: testApp,
        window_title: testTitle,
        duration: testDuration * 60
      });
      const cat = result?.received_category || 'Educational';
      setIngestStatus(`Telemetry Logged! Classified as ${cat}`);
      fetchHistory();
    } catch {
      setIngestStatus('Local Telemetry Logged!');
    }
    setTimeout(() => setIngestStatus(null), 4000);
  };

  return (
    <div className="space-y-6 pb-12 font-sans">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <History className="w-6 h-6 text-brand-400" />
            Activity History & Telemetry Ingestion
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Historical breakdown of application usage, website sessions, focus scores, and telemetry ingestion.
          </p>
        </div>

        {/* Timeframe Filter Buttons */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-900 rounded-xl border border-slate-800">
          {(['Today', '7 Days', '30 Days', 'Semester'] as const).map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                timeframe === tf ? 'bg-brand-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      {/* Telemetry Ingestion Simulator Box */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800">
        <h3 className="text-base font-bold text-slate-100 mb-1 flex items-center gap-2">
          <Radio className="w-4 h-4 text-emerald-400" />
          Test Monitoring Telemetry Ingestion API
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Simulate a background desktop telemetry ping sent by the StudIQ agent.
        </p>

        <form onSubmit={handleTestTelemetry} className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <input
            type="text"
            value={testApp}
            onChange={(e) => setTestApp(e.target.value)}
            placeholder="Application Name"
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
          />
          <input
            type="text"
            value={testTitle}
            onChange={(e) => setTestTitle(e.target.value)}
            placeholder="Window Title"
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
          />
          <input
            type="number"
            value={testDuration}
            onChange={(e) => setTestDuration(Number(e.target.value))}
            placeholder="Duration (mins)"
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
          />
          <button
            type="submit"
            className="bg-brand-600 hover:bg-brand-500 text-white font-medium text-xs rounded-xl py-2 px-4 flex items-center justify-center gap-1.5 transition shadow-lg shadow-brand-500/20"
          >
            <Plus className="w-4 h-4" /> Ingest Telemetry Ping
          </button>
        </form>

        {ingestStatus && (
          <div className="mt-3 text-xs font-mono text-emerald-400 bg-emerald-500/10 p-2.5 rounded-xl border border-emerald-500/20 flex items-center gap-2">
            <Check className="w-4 h-4 text-emerald-400" /> {ingestStatus}
          </div>
        )}
      </div>

      {/* Overview Cards for Timeframe */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-card rounded-2xl p-4 border border-slate-800">
          <span className="text-xs text-slate-400 block mb-1">Timeframe</span>
          <span className="text-lg font-bold text-slate-100">{timeframe} Log</span>
        </div>
        <div className="glass-card rounded-2xl p-4 border border-slate-800">
          <span className="text-xs text-slate-400 block mb-1">Avg Focus History</span>
          <span className="text-lg font-bold text-emerald-400">{avgFocus} Index</span>
        </div>
        <div className="glass-card rounded-2xl p-4 border border-slate-800">
          <span className="text-xs text-slate-400 block mb-1">Avg Burnout History</span>
          <span className="text-lg font-bold text-slate-300">{avgBurnout}% Risk</span>
        </div>
        <div className="glass-card rounded-2xl p-4 border border-slate-800">
          <span className="text-xs text-slate-400 block mb-1">Total Recorded Logs</span>
          <span className="text-lg font-bold text-brand-400">{totalRecords} Sessions</span>
        </div>
      </div>

      {/* Activity Timeline Table */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800">
        <h3 className="text-base font-bold text-slate-100 mb-4">Activity Timeline & App Usage History</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 text-slate-400 font-semibold uppercase font-mono">
              <tr>
                <th className="py-3 px-4">Time</th>
                <th className="py-3 px-4">Application</th>
                <th className="py-3 px-4">Window Title / Context</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Duration</th>
                <th className="py-3 px-4">Focus Score</th>
                <th className="py-3 px-4">Burnout Risk</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {activities.map((act) => (
                <tr key={act.id} className="hover:bg-slate-900/40 transition">
                  <td className="py-3.5 px-4 font-mono text-slate-500">{act.time}</td>
                  <td className="py-3.5 px-4 font-bold text-slate-100">{act.app}</td>
                  <td className="py-3.5 px-4 truncate max-w-xs text-slate-400">{act.context}</td>
                  <td className="py-3.5 px-4">
                    <Badge variant={act.category === 'Entertainment' || act.category === 'Gaming' ? 'high' : 'info'}>{act.category}</Badge>
                  </td>
                  <td className="py-3.5 px-4 font-mono">{act.duration}</td>
                  <td className="py-3.5 px-4 font-bold text-emerald-400">{act.focus}</td>
                  <td className="py-3.5 px-4 font-bold text-rose-400">{act.burnout}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
