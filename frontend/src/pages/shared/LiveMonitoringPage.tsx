import React, { useState, useEffect } from 'react';
import { CircularProgress } from '../../components/ui/CircularProgress';
import { Badge } from '../../components/Badge';
import { MonitoringService, ActivityCategory } from '../../services/monitoringService';
import { WarningModal } from '../../components/monitoring/WarningModal';
import { SessionLockModal } from '../../components/monitoring/SessionLockModal';
import { FocusScoreModal } from '../../components/monitoring/FocusScoreModal';
import { BurnoutScoreModal } from '../../components/monitoring/BurnoutScoreModal';
import { Modal } from '../../components/Modal';
import { getReadableAppName } from '../../utils/helpers';
import { useToast } from '../../context/ToastContext';
import {
  Radio,
  Laptop,
  Globe,
  Clock,
  Sparkles,
  AlertTriangle,
  Lightbulb,
  CheckCircle2,
  Tv,
  Gamepad2,
  GraduationCap,
  History,
  ShieldCheck,
  Shield,
  RefreshCw,
  Download,
  Eye,
  Search,
  X
} from 'lucide-react';

import { ApiService, API_BASE_URL } from '../../services/api';
import { AgentBridgeService } from '../../services/monitoringService';

interface LiveTelemetryData {
  current_application: string;
  window_title: string;
  website_url: string;
  category: ActivityCategory;
  confidence: number;
  session_duration: number;
  educational_duration: number;
  productive_duration: number;
  entertainment_duration: number;
  gaming_duration: number;
  utilities_duration: number;
  idle_seconds: number;
  focus_score: number;
  focus_probability?: number;
  burnout_probability?: number;
  focus_breakdown?: any;
  burnout_breakdown?: any;
  current_activity_started_at: string;
  agent_connected: boolean;
  entertainment_status?: {
    show_popup: boolean;
    cumulative_mins: number;
    warnings_remaining: number;
    ignored_warning_count: number;
  };
  recent_logs?: Array<{
    id: number;
    application: string;
    window_title: string;
    website: string;
    category: string;
    confidence: number;
    timestamp: string;
    duration: number;
  }>;
}

export const LiveMonitoringPage: React.FC = () => {
  const { showToast } = useToast();
  const monitoringService = MonitoringService.getInstance();

  const [telemetry, setTelemetry] = useState<LiveTelemetryData>({
    current_application: 'Desktop Agent',
    window_title: 'Connecting to Monitoring Service...',
    website_url: '',
    category: 'Educational',
    confidence: 0.85,
    session_duration: 0,
    educational_duration: 0,
    productive_duration: 0,
    entertainment_duration: 0,
    gaming_duration: 0,
    utilities_duration: 0,
    idle_seconds: 0,
    focus_score: 80,
    burnout_probability: 15,
    current_activity_started_at: 'N/A',
    agent_connected: false
  });

  const [isWarningOpen, setIsWarningOpen] = useState(false);
  const [isLockOpen, setIsLockOpen] = useState(false);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [isFocusModalOpen, setIsFocusModalOpen] = useState(false);
  const [isBurnoutModalOpen, setIsBurnoutModalOpen] = useState(false);
  const [ignoredWarningCount, setIgnoredWarningCount] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Timeline Filtering & Search
  const [timelineFilter, setTimelineFilter] = useState<'All' | 'Educational' | 'Productive' | 'Entertainment' | 'Gaming'>('All');
  const [timelineSearch, setTimelineSearch] = useState('');

  const fetchTelemetry = async (manual: boolean = false) => {
    if (manual) setIsRefreshing(true);
    try {
      // 1. Check local agent bridge or backend agent connection status
      const bridgeStatus = await AgentBridgeService.checkBridgeStatus();
      const isBridgeActive = Boolean(bridgeStatus && (bridgeStatus.bridge_status === 'active' || bridgeStatus.agent_running || (bridgeStatus as any).running));

      const res = await fetch(`${API_BASE_URL}/monitoring/current-activity`, { headers: ApiService.getHeaders() });
      if (res.ok) {
        const data: LiveTelemetryData = await res.json();
        data.agent_connected = isBridgeActive || Boolean(data.agent_connected);
        setTelemetry(data);

        if (data.entertainment_status?.show_popup) {
          setIsWarningOpen(true);
          setIgnoredWarningCount(data.entertainment_status.ignored_warning_count || 0);
        }
        if (manual) showToast('Live Telemetry Stream Refreshed!', 'success');
      } else if (isBridgeActive) {
        setTelemetry(prev => ({ ...prev, agent_connected: true }));
      }
    } catch (e) {
      console.error("Failed to fetch live telemetry:", e);
      if (manual) showToast('Unable to connect to Desktop Agent backend service', 'error');
    } finally {
      if (manual) setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchTelemetry();
    const interval = setInterval(() => fetchTelemetry(false), 3000);
    return () => clearInterval(interval);
  }, []);

  const handleContinueStudying = async () => {
    setIsWarningOpen(false);
    try {
      await fetch(`${API_BASE_URL}/monitoring/popup-action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: 1, action: 'continue_studying' })
      });
    } catch (e) {}
    monitoringService.resetWarningCount();
    setIgnoredWarningCount(0);
    showToast('Switched back to Deep Study Session!', 'success');
  };

  const handleIgnoreWarning = async () => {
    setIsWarningOpen(false);
    try {
      await fetch(`${API_BASE_URL}/monitoring/popup-action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: 1, action: 'ignore' })
      });
    } catch (e) {}
    const result = monitoringService.handleIgnoreWarning();
    setIgnoredWarningCount(result.count);

    if (result.shouldLock) {
      setIsLockOpen(true);
      showToast('Session Locked! Parent notification dispatched.', 'error');
    } else {
      showToast(`Warning Ignored (${result.count}/5). Limit: 5 max.`, 'warning');
    }
  };

  const handleAcknowledgeAndResume = () => {
    setIsLockOpen(false);
    monitoringService.resetWarningCount();
    setIgnoredWarningCount(0);
    showToast('Study Session Resumed. Monitoring Active.', 'success');
  };

  const simulateActivity = async (activityType: 'coding' | 'research' | 'youtube' | 'gaming') => {
    let payload = {};
    if (activityType === 'coding') {
      payload = {
        student_id: 1,
        application_name: 'Visual Studio Code',
        window_title: 'studiq / main.py',
        website_url: '',
        category: 'Productive',
        confidence: 0.98,
        duration_seconds: 15
      };
    } else if (activityType === 'research') {
      payload = {
        student_id: 1,
        application_name: 'Google Chrome',
        window_title: 'DSA Lecture - Stack and Queue Data Structures',
        website_url: 'https://coursera.org',
        category: 'Educational',
        confidence: 0.95,
        duration_seconds: 15
      };
    } else if (activityType === 'youtube') {
      payload = {
        student_id: 1,
        application_name: 'Google Chrome',
        window_title: 'funny memes - YouTube',
        website_url: 'https://youtube.com/watch?v=123',
        category: 'Entertainment',
        confidence: 0.97,
        duration_seconds: 15
      };
    } else if (activityType === 'gaming') {
      payload = {
        student_id: 1,
        application_name: 'Valorant.exe',
        window_title: 'VALORANT',
        website_url: '',
        category: 'Gaming',
        confidence: 0.99,
        duration_seconds: 15
      };
    }

    try {
      const res = await fetch(`${API_BASE_URL}/monitoring/telemetry`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        showToast(`Simulated active window: ${activityType === 'coding' ? 'VS Code' : activityType === 'research' ? 'Coursera' : activityType === 'youtube' ? 'YouTube' : 'Valorant'}`, 'success');
        fetchTelemetry(); // update view immediately
      }
    } catch (e) {
      showToast('Simulation service unavailable', 'error');
    }
  };

  const handleExportCSV = () => {
    window.open(`${API_BASE_URL}/reports/export/csv/daily`, '_blank');
    showToast('Exporting Daily Monitoring Log CSV...', 'info');
  };

  const formatTimer = (totalSecs: number) => {
    const mins = Math.floor(totalSecs / 60);
    const secs = totalSecs % 60;
    return `${mins}m ${secs < 10 ? '0' : ''}${secs}s`;
  };

  const formatMins = (secs: number) => {
    const m = Math.floor(secs / 60);
    const h = (m / 60).toFixed(1);
    return m >= 60 ? `${h}h` : `${m}m`;
  };

  const isCodingActive = telemetry.category === 'Productive' || telemetry.current_application.toLowerCase().includes('code');
  const isResearchActive = telemetry.category === 'Educational' && !telemetry.current_application.toLowerCase().includes('code');
  const isYouTubeActive = telemetry.category === 'Entertainment' || telemetry.website_url.includes('youtube');
  const isGamingActive = telemetry.category === 'Gaming' || telemetry.current_application.toLowerCase().includes('steam') || telemetry.current_application.toLowerCase().includes('valorant');

  const totalSecsMonitored = (telemetry.educational_duration || 0) + (telemetry.productive_duration || 0) + (telemetry.entertainment_duration || 0) + (telemetry.gaming_duration || 0) + (telemetry.utilities_duration || 0);

  const filteredLogs = (telemetry.recent_logs || []).filter(log => {
    const matchesFilter = timelineFilter === 'All' || log.category === timelineFilter;
    const matchesSearch = !timelineSearch ||
      log.application.toLowerCase().includes(timelineSearch.toLowerCase()) ||
      log.window_title.toLowerCase().includes(timelineSearch.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  return (
    <div className="space-y-6 pb-12 font-sans">
      {/* Header & Hero Title */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Radio className="w-5 h-5 text-emerald-400 animate-pulse" />
            <span className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-widest">
              LIVE BEHAVIOUR INTELLIGENCE • REAL-TIME AGENT TELEMETRY
            </span>
          </div>
          <h1 className="text-2xl font-black text-white">Active Student Monitoring Engine</h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time digital telemetry stream driven live by Windows Desktop Agent.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => fetchTelemetry(true)}
            disabled={isRefreshing}
            className="px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 text-xs font-bold flex items-center gap-1.5 transition disabled:opacity-50"
            title="Refresh Live Telemetry"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-brand-400 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>

          <button
            onClick={() => setIsDetailsOpen(true)}
            className="px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 text-xs font-bold flex items-center gap-1.5 transition"
            title="View Raw Telemetry Details"
          >
            <Eye className="w-3.5 h-3.5 text-emerald-400" />
            View Details
          </button>

          <button
            onClick={handleExportCSV}
            className="px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 text-xs font-bold flex items-center gap-1.5 transition"
            title="Export Activity Log CSV"
          >
            <Download className="w-3.5 h-3.5 text-indigo-400" />
            Export CSV
          </button>

          <div className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 shadow-lg ${
            telemetry.agent_connected
              ? 'bg-emerald-500/15 border border-emerald-500/30 text-emerald-400'
              : 'bg-rose-500/15 border border-rose-500/30 text-rose-400'
          }`}>
            <span className="w-2.5 h-2.5 rounded-full bg-current animate-pulse" />
            {telemetry.agent_connected ? '🟢 Connected' : '🔴 Offline'}
          </div>
        </div>
      </div>

      {/* STRICT PRIVACY GUARANTEE BANNER */}
      <div className="p-4 rounded-2xl bg-slate-900/90 border border-emerald-500/20 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 text-xs">
        <div className="flex items-start gap-3">
          <Shield className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          <div>
            <strong className="block text-slate-100 font-bold text-xs mb-0.5">Strict Privacy Guarantee Notice</strong>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              StudIQ <strong>NEVER</strong> accesses Gallery, Photos, Passwords, Bank Applications, Private Messages, or Private Files. Only high-level app window titles and time duration metadata are monitored.
            </p>
          </div>
        </div>
        <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full shrink-0 border border-emerald-500/20">
          Zero-Knowledge Encrypted
        </span>
      </div>

      {/* AUTOMATIC ACTIVITY CARDS (NOW CLICKABLE FOR SIMULATION OVERRIDE) */}
      <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2 font-mono">
            <ShieldCheck className="w-3.5 h-3.5 text-brand-400" /> Live Desktop Activity Classification
          </span>
          <span className="text-[11px] text-slate-500 font-mono">Click to simulate different agent telemetry payloads</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
          <button
            onClick={() => simulateActivity('coding')}
            className={`p-3 rounded-xl border text-xs font-bold flex items-center justify-center gap-2 cursor-pointer hover:scale-[1.02] active:scale-[0.98] transition-all ${
              isCodingActive
                ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300 shadow ring-2 ring-emerald-500/30'
                : 'bg-slate-950 border-slate-800 text-slate-500 hover:text-slate-350 opacity-60 hover:opacity-90'
            }`}
          >
            <Laptop className="w-4 h-4 text-emerald-400" /> Deep Coding Flow
          </button>

          <button
            onClick={() => simulateActivity('research')}
            className={`p-3 rounded-xl border text-xs font-bold flex items-center justify-center gap-2 cursor-pointer hover:scale-[1.02] active:scale-[0.98] transition-all ${
              isResearchActive
                ? 'bg-brand-500/20 border-brand-500 text-brand-300 shadow ring-2 ring-brand-500/30'
                : 'bg-slate-950 border-slate-800 text-slate-500 hover:text-slate-350 opacity-60 hover:opacity-90'
            }`}
          >
            <GraduationCap className="w-4 h-4 text-brand-400" /> Academic Research
          </button>

          <button
            onClick={() => simulateActivity('youtube')}
            className={`p-3 rounded-xl border text-xs font-bold flex items-center justify-center gap-2 cursor-pointer hover:scale-[1.02] active:scale-[0.98] transition-all ${
              isYouTubeActive
                ? 'bg-amber-500/20 border-amber-500 text-amber-300 shadow ring-2 ring-amber-500/30'
                : 'bg-slate-950 border-slate-800 text-slate-500 hover:text-slate-350 opacity-60 hover:opacity-90'
            }`}
          >
            <Tv className="w-4 h-4 text-amber-400" /> YouTube Distraction
          </button>

          <button
            onClick={() => simulateActivity('gaming')}
            className={`p-3 rounded-xl border text-xs font-bold flex items-center justify-center gap-2 cursor-pointer hover:scale-[1.02] active:scale-[0.98] transition-all ${
              isGamingActive
                ? 'bg-rose-500/20 border-rose-500 text-rose-300 shadow ring-2 ring-rose-500/30'
                : 'bg-slate-950 border-slate-800 text-slate-500 hover:text-slate-350 opacity-60 hover:opacity-90'
            }`}
          >
            <Gamepad2 className="w-4 h-4 text-rose-400" /> Late Night Gaming
          </button>
        </div>
      </div>

      {/* TOP METRICS & GAUGES */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* 1. Live Status Card */}
        <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Monitoring Status</span>
          <div className="my-3">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border border-emerald-500/30 text-emerald-400 bg-emerald-500/10">
              <span className="w-2 h-2 rounded-full bg-current animate-pulse" />
              {telemetry.category} Session
            </span>
          </div>
          <span className="text-[11px] text-slate-500 font-mono flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Confidence: {(telemetry.confidence * 100).toFixed(0)}%
          </span>
        </div>

        {/* 2. Focus Score */}
        <div
          onClick={() => setIsFocusModalOpen(true)}
          className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col items-center justify-center text-center cursor-pointer hover:border-brand-500/50 transition group"
          title="Click to view Focus Score Calculation Formula & Telemetry Breakdown"
        >
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 group-hover:text-brand-400 transition">Live Focus Index ℹ️</span>
          <CircularProgress value={Math.round(telemetry.focus_score)} label="FOCUS" type="focus" />
        </div>

        {/* 3. Burnout Risk */}
        <div
          onClick={() => setIsBurnoutModalOpen(true)}
          className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col items-center justify-center text-center cursor-pointer hover:border-rose-500/50 transition group"
          title="Click to view Burnout Risk Contributing Factors & Telemetry Breakdown"
        >
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 group-hover:text-rose-400 transition">Burnout Probability ℹ️</span>
          <CircularProgress value={Math.round(telemetry.burnout_probability ?? 0)} label="RISK" type="burnout" />
        </div>


        {/* 4. Active Session Time */}
        <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Current Session</span>
            <Clock className="w-4 h-4 text-brand-400" />
          </div>
          <div className="my-2">
            <div className="text-2xl font-black text-white font-mono">{formatTimer(telemetry.session_duration)}</div>
            <p className="text-[11px] text-slate-400">Started at {telemetry.current_activity_started_at}</p>
          </div>
          <Badge variant={telemetry.category === 'Entertainment' || telemetry.category === 'Gaming' ? 'high' : 'info'}>
            Category: {telemetry.category}
          </Badge>
        </div>
      </div>

      {/* ACTIVE APP & WEB TELEMETRY DETAIL */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Application & Window Card */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Laptop className="w-5 h-5 text-brand-400" /> Current Application Window
            </h3>
            <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">
              Live OS Capture
            </span>
          </div>

          <div className="space-y-3">
            <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase font-mono block mb-1">Process Name</span>
              <span className="text-sm font-bold text-white flex items-center gap-2">
                <span>{getReadableAppName(telemetry.current_application)}</span>
                <span className="text-xs text-slate-400 font-normal">({telemetry.current_application})</span>
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase font-mono block mb-1">Active Window Title</span>
              <span className="text-xs font-mono text-slate-200 break-all">{telemetry.window_title}</span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase font-mono block mb-1">Domain / Web Address</span>
              <span className="text-xs font-mono text-brand-400 flex items-center gap-1.5">
                <Globe className="w-3.5 h-3.5" /> {telemetry.website_url || 'N/A (Desktop App)'}
              </span>
            </div>
          </div>
        </div>

        {/* AI Classification & Real-Time Intelligence */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-emerald-400" /> AI Classification Engine
              </h3>
              <span className="text-[11px] font-mono text-slate-400">Confidence: {(telemetry.confidence * 100).toFixed(1)}%</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
              <div className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" /> Real Telemetry Analysis
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Active execution window classified as <strong>{telemetry.category}</strong>. Idle time: {telemetry.idle_seconds}s.
              </p>
            </div>

            {telemetry.entertainment_status && telemetry.entertainment_status.cumulative_mins > 0 && (
              <div className="mt-3 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400" />
                <span>Cumulative Entertainment: {telemetry.entertainment_status.cumulative_mins} mins (Limit: 15m interval warning)</span>
              </div>
            )}
          </div>

          <div className="p-4 rounded-xl bg-brand-500/10 border border-brand-500/20 text-brand-300 text-xs flex items-start gap-2.5">
            <Lightbulb className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <strong className="block text-slate-200 font-semibold mb-0.5">Smart Recommendation</strong>
              {telemetry.focus_score >= 80 ? 'Excellent deep focus! Maintain current study momentum.' : 'Consider closing background entertainment tabs to improve focus.'}
            </div>
          </div>
        </div>
      </div>

      {/* TODAY'S TIMELINE BAR & LIVE LOGS WITH FILTERS */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <History className="w-5 h-5 text-brand-400" /> Today's Activity Timeline Breakdown
          </h3>

          {/* Timeline Search & Filter Controls */}
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <div className="relative flex-1 sm:w-48">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search log..."
                value={timelineSearch}
                onChange={(e) => setTimelineSearch(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500 font-mono"
              />
              {timelineSearch && (
                <button onClick={() => setTimelineSearch('')} className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white">
                  <X className="w-3 h-3" />
                </button>
              )}
            </div>

            <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800 text-[11px] font-semibold">
              {(['All', 'Educational', 'Productive', 'Entertainment', 'Gaming'] as const).map((cat) => (
                <button
                  key={cat}
                  onClick={() => setTimelineFilter(cat)}
                  className={`px-2.5 py-1 rounded-lg transition ${
                    timelineFilter === cat
                      ? 'bg-brand-600 text-white shadow'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Visual Segment Bar */}
        <div className="w-full h-4 rounded-full bg-slate-900 overflow-hidden flex p-0.5 gap-0.5">
          <div className="h-full bg-emerald-500 rounded-l-full" style={{ width: `${totalSecsMonitored ? ((telemetry.educational_duration / totalSecsMonitored) * 100) : 50}%` }} title="Educational" />
          <div className="h-full bg-brand-500" style={{ width: `${totalSecsMonitored ? ((telemetry.productive_duration / totalSecsMonitored) * 100) : 30}%` }} title="Productive" />
          <div className="h-full bg-amber-500" style={{ width: `${totalSecsMonitored ? ((telemetry.entertainment_duration / totalSecsMonitored) * 100) : 10}%` }} title="Entertainment" />
          <div className="h-full bg-rose-500 rounded-r-full" style={{ width: `${totalSecsMonitored ? ((telemetry.gaming_duration / totalSecsMonitored) * 100) : 10}%` }} title="Gaming" />
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs pt-2">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-emerald-500" />
            <div>
              <span className="block font-bold text-slate-200">{formatMins(telemetry.educational_duration || 0)}</span>
              <span className="text-[11px] text-slate-400">Educational</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-brand-500" />
            <div>
              <span className="block font-bold text-slate-200">{formatMins(telemetry.productive_duration || 0)}</span>
              <span className="text-[11px] text-slate-400">Productive</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-amber-500" />
            <div>
              <span className="block font-bold text-slate-200">{formatMins(telemetry.entertainment_duration || 0)}</span>
              <span className="text-[11px] text-slate-400">Entertainment</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-rose-500" />
            <div>
              <span className="block font-bold text-slate-200">{formatMins(telemetry.gaming_duration || 0)}</span>
              <span className="text-[11px] text-slate-400">Gaming</span>
            </div>
          </div>
        </div>

        {/* Timeline Log Sequence */}
        <div className="pt-4 border-t border-slate-800 space-y-2 text-xs font-mono">
          {filteredLogs.length > 0 ? (
            filteredLogs.map((log) => (
              <div key={log.id} className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between text-slate-300 hover:bg-slate-900 transition">
                <span>{log.timestamp} • {log.application} ({log.window_title.slice(0, 45)})</span>
                <span className={log.category === 'Educational' || log.category === 'Productive' ? 'text-emerald-400 font-semibold' : 'text-amber-400 font-semibold'}>
                  {log.category} ({log.duration}s)
                </span>
              </div>
            ))
          ) : (
            <div className="p-4 text-center text-slate-500 font-sans text-xs">
              {timelineSearch || timelineFilter !== 'All' ? 'No telemetry logs match current filter criteria.' : 'Listening for Desktop Agent activity snapshots...'}
            </div>
          )}
        </div>
      </div>

      {/* Raw Telemetry View Details Modal */}
      <Modal
        isOpen={isDetailsOpen}
        onClose={() => setIsDetailsOpen(false)}
        title="Live Desktop Agent Telemetry Diagnostics"
      >
        <div className="space-y-4 py-2 font-sans text-xs">
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <div className="flex justify-between border-b border-slate-800 pb-2">
              <span className="text-slate-400">Process Executable:</span>
              <span className="font-bold text-white font-mono">{telemetry.current_application}</span>
            </div>
            <div className="flex justify-between border-b border-slate-800 pb-2">
              <span className="text-slate-400">Window Title:</span>
              <span className="font-mono text-slate-200 text-right max-w-xs truncate">{telemetry.window_title}</span>
            </div>
            <div className="flex justify-between border-b border-slate-800 pb-2">
              <span className="text-slate-400">Website URL:</span>
              <span className="font-mono text-brand-400">{telemetry.website_url || 'N/A'}</span>
            </div>
            <div className="flex justify-between border-b border-slate-800 pb-2">
              <span className="text-slate-400">Category / Confidence:</span>
              <span className="font-bold text-emerald-400">{telemetry.category} ({(telemetry.confidence * 100).toFixed(0)}%)</span>
            </div>
            <div className="flex justify-between border-b border-slate-800 pb-2">
              <span className="text-slate-400">Idle Seconds / Session Duration:</span>
              <span className="font-mono text-slate-300">{telemetry.idle_seconds}s / {formatTimer(telemetry.session_duration)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Agent Health:</span>
              <span className="text-emerald-400 font-bold">{telemetry.agent_connected ? 'Active Ping (Every 30s)' : 'Disconnected'}</span>
            </div>
          </div>

          <button
            onClick={() => setIsDetailsOpen(false)}
            className="w-full py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-bold transition shadow-lg"
          >
            Close Diagnostics
          </button>
        </div>
      </Modal>

      {/* Warning Popup Modal */}
      <WarningModal
        isOpen={isWarningOpen}
        ignoredCount={ignoredWarningCount}
        onContinueStudying={handleContinueStudying}
        onIgnore={handleIgnoreWarning}
      />

      {/* Session Lock Modal */}
      <SessionLockModal
        isOpen={isLockOpen}
        onAcknowledgeAndResume={handleAcknowledgeAndResume}
      />

      {/* Focus Score Breakdown Modal */}
      <FocusScoreModal
        isOpen={isFocusModalOpen}
        onClose={() => setIsFocusModalOpen(false)}
        focusScore={Math.round(telemetry.focus_score)}
        breakdown={telemetry.focus_breakdown}
      />

      {/* Burnout Risk Breakdown Modal */}
      <BurnoutScoreModal
        isOpen={isBurnoutModalOpen}
        onClose={() => setIsBurnoutModalOpen(false)}
        burnoutScore={Math.round(telemetry.burnout_probability ?? 0)}
        breakdown={telemetry.burnout_breakdown}
      />
    </div>
  );
};




