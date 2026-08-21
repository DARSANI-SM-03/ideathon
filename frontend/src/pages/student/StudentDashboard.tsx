import React, { useEffect, useState } from 'react';
import { ApiService, API_BASE_URL } from '../../services/api';
import { StudentDashboardData } from '../../types';
import { CircularProgress } from '../../components/ui/CircularProgress';
import { StudentOnboardingWizard } from '../../components/onboarding/StudentOnboardingWizard';
import { FocusScoreModal } from '../../components/monitoring/FocusScoreModal';
import { BurnoutScoreModal } from '../../components/monitoring/BurnoutScoreModal';
import { useNavigate } from 'react-router-dom';
import { getReadableAppName } from '../../utils/helpers';
import { useAuth } from '../../context/AuthContext';

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip
} from 'recharts';
import {
  Clock,
  Tv,
  GraduationCap,
  Laptop,
  Activity,
  Lightbulb,
  AlertTriangle,
  FileText,
  Radio,
  ArrowRight,
  ShieldCheck,
  Brain
} from 'lucide-react';

interface EntertainmentStatus {
  student_id: number;
  timer_status: 'Active' | 'Paused';
  continuous_entertainment_secs: number;
  continuous_entertainment_mins: number;
  today_entertainment_secs: number;
  today_entertainment_mins: number;
  display_str: string;
  is_popup_active: boolean;
  popup_message: string;
  ignored_warning_count: number;
}

interface TimelineItem {
  id?: number;
  time: string;
  app: string;
  title: string;
  website_url?: string;
  category: string;
  duration_secs?: number;
}

interface WeeklyAnalyticsItem {
  day: string;
  focus: number;
  burnout: number;
  studyHours: number;
  entertainmentMins: number;
}

interface CurrentActivityData {
  current_application?: string;
  window_title?: string;
  website_url?: string;
  category?: string;
  confidence?: number;
  agent_connected?: boolean;
}

export const StudentDashboard: React.FC = () => {
  const { user } = useAuth();
  const [data, setData] = useState<StudentDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const navigate = useNavigate();

  // Real-time live telemetry state
  const [agentConnected, setAgentConnected] = useState<boolean>(true);
  const [currentActivity, setCurrentActivity] = useState<CurrentActivityData | null>(null);
  const [liveFocusScore, setLiveFocusScore] = useState<number>(85);
  const [liveBurnoutScore, setLiveBurnoutScore] = useState<number>(18);
  const [liveBurnoutRisk, setLiveBurnoutRisk] = useState<string>('Low');
  const [burnoutReasons, setBurnoutReasons] = useState<string[]>([]);
  const [focusExplanations, setFocusExplanations] = useState<string[]>([]);
  const [lastUpdatedSecs, setLastUpdatedSecs] = useState<number>(0);
  const [liveTimeline, setLiveTimeline] = useState<TimelineItem[]>([]);
  const [weeklyTrend, setWeeklyTrend] = useState<WeeklyAnalyticsItem[]>([]);

  const [isFocusModalOpen, setIsFocusModalOpen] = useState(false);
  const [isBurnoutModalOpen, setIsBurnoutModalOpen] = useState(false);
  const [focusBreakdown, setFocusBreakdown] = useState<any>(null);
  const [burnoutBreakdown, setBurnoutBreakdown] = useState<any>(null);


  // Entertainment duration tracking & popup state
  const [entertainmentStatus, setEntertainmentStatus] = useState<EntertainmentStatus>({
    student_id: user?.id || 1,
    timer_status: 'Paused',
    continuous_entertainment_secs: 0,
    continuous_entertainment_mins: 0,
    today_entertainment_secs: 0,
    today_entertainment_mins: 0,
    display_str: '0 min',
    is_popup_active: false,
    popup_message: '',
    ignored_warning_count: 0
  });

  const handlePopupAction = (action: 'continue_studying' | 'ignore') => {
    fetch(`${API_BASE_URL}/monitoring/popup-action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: user?.id || 1, action })
    })
      .then(r => r.json())
      .then(() => {
        fetch(`${API_BASE_URL}/monitoring/entertainment-status`)
          .then(r => r.json())
          .then(res => setEntertainmentStatus(res))
          .catch(() => {});
      })
      .catch(() => {});
  };

  useEffect(() => {
    const isMonitoringEnabled = localStorage.getItem('studiq_monitoring_enabled') === 'true';
    if (!isMonitoringEnabled) {
      setShowOnboarding(true);
    }

    const studentIdentifier = user?.user_identifier || 'STU-2026-001';
    ApiService.fetchStudentDashboard(studentIdentifier).then((res) => {
      setData(res);
      if (res.focus_score) setLiveFocusScore(res.focus_score);
      if (res.burnout_score) setLiveBurnoutScore(res.burnout_score);
      if (res.weekly_analytics) {
        setWeeklyTrend(res.weekly_analytics.map(w => ({
          day: w.day,
          focus: w.focus,
          burnout: w.burnout,
          studyHours: w.study_hours,
          entertainmentMins: 0
        })));
      }

      setLoading(false);
    });

    // Initial fetch of timeline & analytics
    fetch(`${API_BASE_URL}/monitoring/timeline`)
      .then(r => r.json())
      .then(res => setLiveTimeline(res.timeline || []))
      .catch(() => {});

    fetch(`${API_BASE_URL}/monitoring/analytics`)
      .then(r => r.json())
      .then(res => {
        if (Array.isArray(res) && res.length > 0) {
          setWeeklyTrend(res.map(d => ({
            day: d.day,
            focus: d.focusScore || 85,
            burnout: d.burnoutScore || 20,
            studyHours: d.studyHours || 4.5,
            entertainmentMins: d.entertainmentMins || 20
          })));
        }
      })
      .catch(() => {});

    // 3-second live polling loop
    const pollInterval = setInterval(() => {
      // 1. Poll Agent Connection Status
      fetch(`${API_BASE_URL}/monitoring/agent-status`)
        .then(r => r.json())
        .then(res => {
          setAgentConnected(res.connected);
          if (res.last_ping_seconds_ago !== null && res.last_ping_seconds_ago !== undefined) {
            setLastUpdatedSecs(Math.round(res.last_ping_seconds_ago));
          }
          if (res.entertainment_status) setEntertainmentStatus(res.entertainment_status);
        })
        .catch(() => setAgentConnected(false));

      // 2. Poll Current Monitored Activity
      fetch(`${API_BASE_URL}/monitoring/current-activity`)
        .then(r => r.json())
        .then(res => {
          setCurrentActivity(res);
          if (res.entertainment_status) setEntertainmentStatus(res.entertainment_status);
          if (res.focus_breakdown) setFocusBreakdown(res.focus_breakdown);
          if (res.burnout_breakdown) setBurnoutBreakdown(res.burnout_breakdown);
          if (res.focus_score) setLiveFocusScore(res.focus_score);
          if (res.burnout_probability) setLiveBurnoutScore(res.burnout_probability);
        })
        .catch(() => {});


      // 3. Poll Focus Score
      fetch(`${API_BASE_URL}/monitoring/focus-score`)
        .then(r => r.json())
        .then(res => {
          if (res.focus_score !== undefined) setLiveFocusScore(res.focus_score);
          if (res.explanation) setFocusExplanations(res.explanation);
        })
        .catch(() => {});

      // 4. Poll Burnout Risk
      fetch(`${API_BASE_URL}/monitoring/burnout`)
        .then(r => r.json())
        .then(res => {
          if (res.burnout_score !== undefined) setLiveBurnoutScore(res.burnout_score);
          if (res.risk_level) setLiveBurnoutRisk(res.risk_level);
          if (res.reasons) setBurnoutReasons(res.reasons);
        })
        .catch(() => {});

      // 5. Poll Entertainment Status
      fetch(`${API_BASE_URL}/monitoring/entertainment-status`)
        .then(r => r.json())
        .then(res => setEntertainmentStatus(res))
        .catch(() => {});

      // 6. Poll Timeline
      fetch(`${API_BASE_URL}/monitoring/timeline`)
        .then(r => r.json())
        .then(res => {
          if (res.timeline && res.timeline.length > 0) {
            setLiveTimeline(res.timeline);
          }
        })
        .catch(() => {});
    }, 3000);

    return () => clearInterval(pollInterval);
  }, [user]);

  if (loading || !data) {
    return (
      <div className="p-12 text-center text-slate-400">
        <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        Syncing Live Desktop Agent Telemetry...
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-12 font-sans relative">
      {/* Onboarding Wizard Modal */}
      {showOnboarding && (
        <StudentOnboardingWizard onComplete={() => setShowOnboarding(false)} />
      )}

      {/* HEALTHY DIGITAL USAGE POPUP MODAL */}
      {entertainmentStatus.is_popup_active && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
          <div className="bg-slate-900 border border-rose-500/40 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-5">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400">
                <Tv className="w-6 h-6 animate-bounce" />
              </div>
              <div>
                <h3 className="text-lg font-black text-white">Healthy Digital Usage</h3>
                <span className="text-xs font-mono text-rose-400">Continuous Screen Time Alert</span>
              </div>
            </div>

            <p className="text-sm text-slate-300 leading-relaxed font-medium">
              You have been continuously using entertainment applications for 15 minutes.
            </p>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => handlePopupAction('continue_studying')}
                className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-slate-950 text-xs font-bold transition shadow-lg shadow-emerald-500/20"
              >
                Continue Studying
              </button>
              <button
                onClick={() => handlePopupAction('ignore')}
                className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold border border-slate-700 transition"
              >
                Ignore
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Welcome Header */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-bold border ${
              agentConnected
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                : 'bg-rose-500/10 text-rose-400 border-rose-500/30 animate-pulse'
            }`}>
              {agentConnected ? '🟢 Desktop Agent Connected' : '🔴 Desktop Agent Offline'}
            </span>
            <span className="text-[11px] font-mono text-slate-400">
              • Last Sync: {lastUpdatedSecs <= 2 ? 'Just now' : `${lastUpdatedSecs}s ago`}
            </span>
          </div>
          <h1 className="text-2xl font-black text-white flex items-center gap-2">
            Welcome back, {user?.name || data.name} 👋
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Dept of {data.department} • Semester {data.semester} • Student ID: <span className="font-mono text-brand-400">{data.student_id}</span>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/student/monitoring')}
            className="px-4 py-2.5 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-xs font-bold flex items-center gap-2 transition"
          >
            <Radio className="w-4 h-4 animate-pulse" /> Live Telemetry Dashboard →
          </button>
        </div>
      </div>

      {/* CURRENT MONITORED APPLICATION & WINDOW TITLE CARD */}
      <div className="glass-card rounded-2xl p-5 border border-brand-500/30 bg-brand-950/20 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-start md:items-center gap-3.5 min-w-0">
          <div className="w-11 h-11 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-400 font-bold shrink-0 mt-0.5 md:mt-0">
            <Laptop className="w-6 h-6 animate-pulse" />
          </div>
          <div className="min-w-0">
            <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
              Currently Monitored Application & Window Title
            </div>
            {agentConnected && currentActivity && (currentActivity.current_application || currentActivity.window_title) ? (
              <div className="space-y-0.5">
                <div className="text-sm font-bold text-white flex items-center gap-2">
                  <span>{getReadableAppName(currentActivity.current_application)}</span>
                  {currentActivity.current_application && (
                    <span className="text-[10px] font-mono text-slate-400 font-normal">({currentActivity.current_application})</span>
                  )}
                </div>
                {currentActivity.window_title ? (
                  <div
                    className="text-xs text-slate-300 font-normal truncate max-w-xl"
                    title={currentActivity.window_title}
                  >
                    {currentActivity.window_title}
                  </div>
                ) : (
                  <div className="text-xs text-slate-500 italic">
                    No active window title
                  </div>
                )}
              </div>
            ) : (
              <div className="text-sm font-semibold text-slate-400 italic mt-0.5">
                No active application
              </div>
            )}
          </div>
        </div>

        {agentConnected && currentActivity && currentActivity.category && (
          <div className="flex items-center gap-2 shrink-0">
            <span className={`px-3 py-1 rounded-full text-xs font-bold font-mono border ${
              currentActivity.category === 'Educational' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' :
              currentActivity.category === 'Productive' ? 'bg-blue-500/10 text-blue-400 border-blue-500/30' :
              currentActivity.category === 'Entertainment' ? 'bg-purple-500/10 text-purple-400 border-purple-500/30' :
              currentActivity.category === 'Gaming' ? 'bg-rose-500/10 text-rose-400 border-rose-500/30' :
              'bg-amber-500/10 text-amber-400 border-amber-500/30'
            }`}>
              {currentActivity.category}
            </span>
            <span className="text-[11px] font-mono text-slate-400">
              ({Math.round(currentActivity.confidence ? currentActivity.confidence * 100 : 95)}% AI Confidence)
            </span>
          </div>
        )}
      </div>

      {/* TOP GAUGES & TELEMETRY TIME CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* 1. Focus Score Ring */}
        <div
          onClick={() => setIsFocusModalOpen(true)}
          className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col items-center justify-center text-center cursor-pointer hover:border-brand-500/50 transition group"
          title="Click to view Focus Score Calculation Formula & Telemetry Breakdown"
        >
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 group-hover:text-brand-400 transition">Focus Score ℹ️</span>
          <CircularProgress value={liveFocusScore} label="WELLNESS" type="focus" />
        </div>

        {/* 2. Burnout Risk Ring */}
        <div
          onClick={() => setIsBurnoutModalOpen(true)}
          className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col items-center justify-center text-center cursor-pointer hover:border-rose-500/50 transition group"
          title="Click to view Burnout Risk Contributing Factors & Telemetry Breakdown"
        >
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 group-hover:text-rose-400 transition">Burnout Risk ({liveBurnoutRisk}) ℹ️</span>
          <CircularProgress value={liveBurnoutScore} label="FATIGUE" type="burnout" />
        </div>


        {/* 3. Today's Study Time */}
        <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Today's Study Time</span>
            <Clock className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="my-2">
            <div className="text-2xl font-black text-white">{data.today_productive_time_mins} mins</div>
            <p className="text-[11px] text-slate-400 mt-0.5">Educational & Productive Telemetry</p>
          </div>
          <span className="text-[11px] text-emerald-400 font-medium">Accumulated from Desktop Agent</span>
        </div>

        {/* 4. Entertainment Time Today */}
        <div className="glass-card rounded-2xl p-5 border border-purple-500/30 bg-purple-950/10 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-purple-300">Entertainment Time Today</span>
            <Tv className="w-4 h-4 text-purple-400" />
          </div>
          <div className="my-2">
            <div className="text-2xl font-black text-white">
              {entertainmentStatus.display_str}
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Continuous: <span className="font-mono text-purple-300 font-bold">{entertainmentStatus.continuous_entertainment_mins} min</span>
            </p>
          </div>
          <div className="flex items-center justify-between">
            <span className={`text-[10px] font-bold font-mono px-2 py-0.5 rounded-full ${
              entertainmentStatus.timer_status === 'Active'
                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30 animate-pulse'
                : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
            }`}>
              {entertainmentStatus.timer_status === 'Active' ? '🔴 Timer Active' : '⏸️ Timer Paused'}
            </span>
          </div>
        </div>
      </div>

      {/* WEEKLY TREND CHART & BURNOUT DIAGNOSTIC REASONS */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Weekly Focus & Entertainment Trend */}
        <div className="lg:col-span-2 glass-card rounded-2xl p-6 border border-slate-800 flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Brain className="w-5 h-5 text-emerald-400" /> Weekly Telemetry Trend
            </h3>
            <span className="text-xs font-mono text-slate-400">7-Day Activity Analysis</span>
          </div>

          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={weeklyTrend.length > 0 ? weeklyTrend : [
                { day: 'Mon', focus: 82, studyHours: 4.5 },
                { day: 'Tue', focus: 88, studyHours: 5.2 },
                { day: 'Wed', focus: 79, studyHours: 3.8 },
                { day: 'Thu', focus: 85, studyHours: 4.9 },
                { day: 'Fri', focus: 90, studyHours: 6.0 },
                { day: 'Sat', focus: 75, studyHours: 3.0 },
                { day: 'Sun', focus: 86, studyHours: 4.2 }
              ]}>
                <defs>
                  <linearGradient id="colorFocus" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="day" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#090d16', borderColor: '#1e293b', borderRadius: '12px', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="focus" stroke="#10b981" fillOpacity={1} fill="url(#colorFocus)" name="Focus Score" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Burnout Risk Diagnostic Reasons (Explain WHY) */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <h3 className="text-base font-bold text-white">Burnout Risk Diagnostics</h3>
          </div>

          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2.5 text-xs">
            <div className="font-bold text-slate-100 flex items-center justify-between">
              <span>Risk Level:</span>
              <span className={`px-2.5 py-0.5 rounded-full text-xs ${
                liveBurnoutRisk === 'Low' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
                liveBurnoutRisk === 'Moderate' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' :
                'bg-rose-500/10 text-rose-400 border border-rose-500/30'
              }`}>
                {liveBurnoutRisk} ({liveBurnoutScore}%)
              </span>
            </div>

            <div className="space-y-1.5 pt-1">
              {(burnoutReasons.length > 0 ? burnoutReasons : [
                "Low risk because:",
                "• Healthy break discipline & study pace."
              ]).map((r, i) => (
                <p key={i} className={`leading-relaxed ${i === 0 ? 'font-semibold text-amber-300' : 'text-slate-300 pl-2'}`}>
                  {r}
                </p>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* LIVE ACTIVITY TIMELINE & RECENT WARNINGS */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Live Activity Timeline */}
        <div className="lg:col-span-2 glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-brand-400" /> Live Telemetry Activity Timeline
            </h3>
            <span className="text-xs font-mono text-slate-400">Sequential DB Telemetry</span>
          </div>

          <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
            {liveTimeline.length > 0 ? (
              liveTimeline.map((item, idx) => (
                <div key={item.id || idx} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono font-bold text-slate-400">{item.time}</span>
                    <div>
                      <div className="text-xs font-bold text-slate-200">{item.app}</div>
                      <div className="text-[11px] text-slate-400 truncate max-w-sm">{item.title}</div>
                    </div>
                  </div>
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono shrink-0 border ${
                    item.category === 'Educational' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                    item.category === 'Productive' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                    item.category === 'Entertainment' ? 'bg-purple-500/10 text-purple-400 border-purple-500/20' :
                    'bg-slate-800 text-slate-300 border-slate-700'
                  }`}>
                    {item.category}
                  </span>
                </div>
              ))
            ) : (
              <div className="p-6 text-center text-xs text-slate-400">
                Awaiting active Desktop Agent telemetry logs...
              </div>
            )}
          </div>
        </div>

        {/* Warning History */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-rose-400" /> Warning History
            </h3>
            <span className="text-xs font-mono text-slate-400">DB Logs</span>
          </div>

          <div className="space-y-3">
            {data.recent_warnings && data.recent_warnings.length > 0 ? (
              data.recent_warnings.map((w: any) => (
                <div key={w.id} className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-1">
                  <div className="flex items-center justify-between font-bold text-rose-400">
                    <span>{w.title}</span>
                    <span className="text-[10px] text-slate-500">{w.created_at}</span>
                  </div>
                  <p className="text-slate-300 text-[11px]">{w.message}</p>
                </div>
              ))
            ) : (
              <div className="p-6 text-center text-xs text-slate-500">
                No active warnings logged today.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Focus Score Breakdown Modal */}
      <FocusScoreModal
        isOpen={isFocusModalOpen}
        onClose={() => setIsFocusModalOpen(false)}
        focusScore={Math.round(liveFocusScore)}
        breakdown={focusBreakdown}
      />

      {/* Burnout Risk Breakdown Modal */}
      <BurnoutScoreModal
        isOpen={isBurnoutModalOpen}
        onClose={() => setIsBurnoutModalOpen(false)}
        burnoutScore={Math.round(liveBurnoutScore)}
        burnoutLevel={liveBurnoutRisk}
        breakdown={burnoutBreakdown}
      />
    </div>
  );
};


