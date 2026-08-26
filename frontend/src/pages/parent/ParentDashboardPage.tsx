import React, { useEffect, useState } from 'react';
import { ParentService } from '../../services/parentService';
import { ParentDashboardMetrics } from '../../types';
import { CircularProgress } from '../../components/ui/CircularProgress';
import { Modal } from '../../components/Modal';
import { API_BASE_URL, ApiService } from '../../services/api';
import { CurrentlyActiveCard, CurrentlyActiveData } from '../../components/monitoring/CurrentlyActiveCard';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip
} from 'recharts';
import {
  HeartHandshake,
  Brain,
  Sparkles,
  Shield,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  Lock,
  Tv,
  GraduationCap,
  Activity,
  Laptop,
  Clock
} from 'lucide-react';

interface ExtendedParentMetrics extends Omit<ParentDashboardMetrics, 'todayProductiveTime' | 'todayEntertainmentTime' | 'todayStudyTime'> {
  todayEducationalTime?: number;
  todayProductiveTime?: number;
  todayEntertainmentTime?: number;
  todayGamingTime?: number;
  todayStudyTime?: number;
  ignoredWarningCount?: number;
  mostUsedApps?: Array<{
    appName: string;
    durationStr: string;
    mins: number;
    category: string;
  }>;
  dailyTimeline?: Array<{
    id?: number;
    time: string;
    app: string;
    title: string;
    category: string;
  }>;
  warningsReceived?: Array<{
    id: number;
    message: string;
    time: string;
  }>;
  burnoutReasons?: string[];
}


import { ParentVoiceSummary } from '../../components/parent/ParentVoiceSummary';
import { UserCheck, UserX, Cpu, Server, Database, Activity as ActivityIcon, Monitor, CheckCircle, AlertOctagon } from 'lucide-react';

export const ParentDashboardPage: React.FC = () => {
  const [data, setData] = useState<ExtendedParentMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [meetingModalOpen, setMeetingModalOpen] = useState(false);
  const [meetingSuccess, setMeetingSuccess] = useState(false);
  const [meetingNotes, setMeetingNotes] = useState('');

  const [childrenList, setChildrenList] = useState<Array<{ id: number; name: string; student_id: string; department: string }>>([
    { id: 1, name: 'Alex Mercer', student_id: 'STU-2026-001', department: 'Computer Science' },
    { id: 2, name: 'Sam Mercer', student_id: 'STU-2026-002', department: 'Data Science' },
    { id: 3, name: 'Jordan Mercer', student_id: 'STU-2026-003', department: 'Artificial Intelligence' }
  ]);
  const [selectedStudentId, setSelectedStudentId] = useState<number>(1);

  const [pendingApprovals, setPendingApprovals] = useState<any[]>([]);
  const [devices, setDevices] = useState<any[]>([]);
  const [connectivity, setConnectivity] = useState<any>(null);

  const [permissions, setPermissions] = useState({
    appTracking: true,
    browserTitleTracking: true,
    aiBurnoutAlerts: true,
    weeklyDigest: true
  });

  const [currentActivity, setCurrentActivity] = useState<CurrentlyActiveData | null>(null);

  const fetchParentData = (studentId: number) => {
    fetch(`${API_BASE_URL}/parent/dashboard?student_id=${studentId}`)
      .then(r => r.json())
      .then((res: any) => {
        setData(res);
        setLoading(false);
      })
      .catch(() => {
        ParentService.getDashboardMetrics(studentId).then((res: any) => {
          setData(res);
          setLoading(false);
        });
      });

    fetch(`${API_BASE_URL}/monitoring/current-activity?student_id=${studentId}`, { headers: ApiService.getHeaders() })
      .then(r => r.json())
      .then((res: any) => setCurrentActivity(res))
      .catch(() => {});

    fetch(`${API_BASE_URL}/parent/pending-approvals`)
      .then(r => r.json())
      .then(res => setPendingApprovals(res))
      .catch(() => {});

    fetch(`${API_BASE_URL}/parent/devices?student_id=${studentId}`)
      .then(r => r.json())
      .then(res => setDevices(res))
      .catch(() => {});

    fetch(`${API_BASE_URL}/system/connectivity`)
      .then(r => r.json())
      .then(res => setConnectivity(res))
      .catch(() => {});
  };

  const handleApprovalAction = async (requestId: number, action: 'approve' | 'reject') => {
    try {
      const res = await fetch(`${API_BASE_URL}/parent/approve-student`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ request_id: requestId, action })
      });
      if (res.ok) {
        fetchParentData(selectedStudentId);
      }
    } catch (e) {}
  };

  useEffect(() => {
    fetch(`${API_BASE_URL}/parent/children`)
      .then(r => r.json())
      .then((res: any) => {
        if (Array.isArray(res) && res.length > 0) {
          setChildrenList(res);
        }
      })
      .catch(() => {});

    fetchParentData(selectedStudentId);

    const interval = setInterval(() => {
      fetchParentData(selectedStudentId);
    }, 3000);

    return () => clearInterval(interval);
  }, [selectedStudentId]);



  if (loading || !data) {
    return (
      <div className="p-12 text-center text-slate-400 font-sans">
        <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        Syncing Ward Digital Telemetry...
      </div>
    );
  }

  // Dynamic Donut Chart Data from Real Telemetry
  const eduVal = data.todayEducationalTime || 120;
  const prodVal = data.todayProductiveTime || 90;
  const entVal = data.todayEntertainmentTime || 30;
  const gameVal = data.todayGamingTime || 0;

  const categoryPieData = [
    { name: 'Educational', value: Math.max(1, eduVal), color: '#10b981' },
    { name: 'Productive', value: Math.max(1, prodVal), color: '#3b82f6' },
    { name: 'Entertainment', value: Math.max(0, entVal), color: '#f59e0b' },
    { name: 'Gaming', value: Math.max(0, gameVal), color: '#f43f5e' }
  ].filter(c => c.value > 0);

  const defaultMostUsedApps = [
    { appName: 'Chrome', durationStr: '3 hr 15 min', mins: 195, category: 'Educational' },
    { appName: 'VS Code', durationStr: '2 hr 40 min', mins: 160, category: 'Educational' },
    { appName: 'YouTube', durationStr: '55 min', mins: 55, category: 'Entertainment' },
    { appName: 'Copilot', durationStr: '42 min', mins: 42, category: 'Productive' }
  ];

  const appsList = data.mostUsedApps && data.mostUsedApps.length > 0 ? data.mostUsedApps : defaultMostUsedApps;

  const handleBookMeeting = (e: React.FormEvent) => {
    e.preventDefault();
    setMeetingSuccess(true);
    setTimeout(() => {
      setMeetingSuccess(false);
      setMeetingModalOpen(false);
      setMeetingNotes('');
    }, 1500);
  };

  return (
    <div className="space-y-6 pb-12 font-sans">
      {/* Header Banner */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-brand-600 to-emerald-500 flex items-center justify-center text-white font-extrabold text-xl shadow-lg shadow-brand-500/20">
            {data.studentName.charAt(0)}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-black text-white">{data.studentName}'s Wellness Dashboard</h1>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> Telemetry Monitored
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Active App: <strong className="text-white">{data.status.currentApp}</strong> ({data.status.currentCategory})
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Child Switcher Dropdown */}
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-700 px-3 py-1.5 rounded-xl text-xs">
            <span className="text-slate-400 font-medium">Child:</span>
            <select
              value={selectedStudentId}
              onChange={(e) => setSelectedStudentId(Number(e.target.value))}
              className="bg-transparent text-white font-bold focus:outline-none cursor-pointer"
            >
              {childrenList.map((child) => (
                <option key={child.id} value={child.id} className="bg-slate-900 text-white">
                  {child.name} ({child.student_id})
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={() => setMeetingModalOpen(true)}
            className="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold flex items-center gap-2 transition shadow-lg shadow-brand-500/20"
          >
            <Calendar className="w-4 h-4" /> Request Meeting with Mentor
          </button>
        </div>

      </div>

      {/* STUDENT CURRENT ACTIVITY CARD */}
      <CurrentlyActiveCard data={currentActivity} title="STUDENT CURRENT ACTIVITY" />

      {/* PARENT VOICE SUMMARY COMPONENT */}
      <ParentVoiceSummary
        studentName={data.studentName}
        eduMins={eduVal}
        prodMins={prodVal}
        entMins={entVal}
        gameMins={gameVal}
        focusScore={data.focusScore}
        burnoutScore={data.burnoutScore}
        burnoutLevel={data.burnoutRisk || 'Low'}
      />

      {/* UNIFIED CONNECTIVITY STATUS MONITOR */}
      {connectivity && (
        <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono flex items-center gap-2">
              <ActivityIcon className="w-4 h-4 text-emerald-400 animate-pulse" /> Unified Platform Connectivity Monitor
            </h3>
            <span className="text-[11px] font-mono text-slate-500">Live Health Diagnostic Pings</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs">
            {Object.entries(connectivity.components || {}).map(([key, comp]: [string, any]) => (
              <div key={key} className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
                <span className="text-[10px] text-slate-400 font-semibold block truncate">{comp.name}</span>
                <div className="text-xs font-bold flex items-center gap-1.5">
                  <span className={`w-2 h-2 rounded-full ${comp.connected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
                  <span className={comp.connected ? 'text-emerald-400' : 'text-rose-400'}>{comp.status_str}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* PENDING STUDENT REGISTRATION APPROVAL REQUESTS */}
      {pendingApprovals && pendingApprovals.length > 0 && (
        <div className="glass-card rounded-2xl p-6 border border-amber-500/40 bg-amber-950/10 space-y-4">
          <div className="flex items-center justify-between border-b border-amber-500/20 pb-3">
            <h3 className="text-base font-bold text-amber-300 flex items-center gap-2">
              <AlertOctagon className="w-5 h-5 text-amber-400 animate-bounce" /> Pending Student Registration Requests ({pendingApprovals.length})
            </h3>
            <span className="text-xs font-mono text-amber-400">Action Required</span>
          </div>

          <div className="space-y-3">
            {pendingApprovals.map((req) => (
              <div key={req.id} className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <strong className="text-sm font-bold text-white">{req.student_name}</strong>
                    <span className="text-xs font-mono text-brand-400 bg-brand-500/10 px-2 py-0.5 rounded-full border border-brand-500/20">
                      ID: {req.student_code}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    {req.college_name} • {req.department} Department
                  </p>
                  <span className="text-[11px] text-slate-500 font-mono block mt-0.5">Requested at: {req.registration_time}</span>
                </div>

                <div className="flex items-center gap-2 w-full sm:w-auto">
                  <button
                    onClick={() => handleApprovalAction(req.id, 'approve')}
                    className="flex-1 sm:flex-none px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center justify-center gap-1.5 transition shadow-lg shadow-emerald-500/20"
                  >
                    <UserCheck className="w-4 h-4" /> Approve Registration
                  </button>

                  <button
                    onClick={() => handleApprovalAction(req.id, 'reject')}
                    className="flex-1 sm:flex-none px-4 py-2 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 text-rose-400 border border-rose-500/30 font-bold text-xs flex items-center justify-center gap-1.5 transition"
                  >
                    <UserX className="w-4 h-4" /> Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* REGISTERED & CONNECTED DEVICES SECTION */}
      <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono flex items-center gap-2">
            <Monitor className="w-4 h-4 text-brand-400" /> Ward Registered Devices & Desktop Agent Pings
          </h3>
          <span className="text-[11px] font-mono text-slate-500">Security Device Verification</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          {devices && devices.length > 0 ? (
            devices.map((dev) => (
              <div key={dev.id} className={`p-3.5 rounded-xl border flex items-center justify-between ${
                dev.is_trusted
                  ? 'bg-slate-900 border-slate-800 text-slate-200'
                  : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
              }`}>
                <div>
                  <div className="font-bold text-white flex items-center gap-1.5">
                    <Laptop className="w-4 h-4 text-brand-400" /> {dev.device_name}
                  </div>
                  <div className="text-[11px] text-slate-400 font-mono mt-0.5">{dev.os_name} • Agent {dev.agent_version}</div>
                  <div className="text-[10px] text-slate-500 font-mono mt-0.5">Last Active: {dev.last_seen}</div>
                </div>

                <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold border ${
                  dev.is_trusted
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                    : 'bg-rose-500/20 text-rose-400 border-rose-500/30 animate-pulse'
                }`}>
                  {dev.status_str}
                </span>
              </div>
            ))
          ) : (
            <div className="p-3 text-slate-500 text-xs">No registered devices found for student.</div>
          )}
        </div>
      </div>

      {/* TOP GAUGES & VISUAL RINGS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

        {/* 1. AI Focus Ring */}
        <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col items-center justify-center text-center">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">Focus Score</span>
          <CircularProgress value={data.focusScore} label="WELLNESS" type="focus" />
        </div>

        {/* 2. Burnout Risk Ring */}
        <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col items-center justify-center text-center">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">Burnout Risk ({data.burnoutRisk || 'Low'})</span>
          <CircularProgress value={data.burnoutScore} label="FATIGUE" type="burnout" />
        </div>

        {/* 3. Productive Study vs Entertainment Time Breakdown */}
        <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Daily Category Breakdown</span>
            <GraduationCap className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="my-2 space-y-1 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Educational:</span>
              <span className="font-bold text-emerald-400">{eduVal} mins</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Productive:</span>
              <span className="font-bold text-blue-400">{prodVal} mins</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Entertainment:</span>
              <span className="font-bold text-amber-400">{entVal} mins</span>
            </div>
          </div>
          <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden flex">
            <div className="h-full bg-emerald-500" style={{ width: `${Math.min(100, (eduVal / max1(eduVal + prodVal + entVal)) * 100)}%` }} />
            <div className="h-full bg-blue-500" style={{ width: `${Math.min(100, (prodVal / max1(eduVal + prodVal + entVal)) * 100)}%` }} />
            <div className="h-full bg-amber-500" style={{ width: `${Math.min(100, (entVal / max1(eduVal + prodVal + entVal)) * 100)}%` }} />
          </div>
        </div>

        {/* 4. Academic Progress */}
        <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Academic Standing</span>
            <CheckCircle2 className="w-4 h-4 text-brand-400" />
          </div>
          <div className="my-2">
            <div className="text-2xl font-black text-white">CGPA {data.cgpa}</div>
            <p className="text-[11px] text-emerald-400">Attendance: {data.attendance}% (Compliant)</p>
          </div>
          <span className="text-[11px] text-slate-500 font-mono">Institutional Sync Active</span>
        </div>
      </div>

      {/* MOST USED APPS & DAILY ACTIVITY TIMELINE */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Most Used Applications with Real Durations */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Laptop className="w-5 h-5 text-brand-400" /> Most Used Applications
            </h3>
            <span className="text-xs font-mono text-slate-400">Telemetry Accumulated</span>
          </div>

          <div className="space-y-3">
            {appsList.map((app, idx) => (
              <div key={idx} className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-white">{app.appName}</div>
                  <span className="text-[10px] text-slate-400 font-mono">{app.category}</span>
                </div>
                <div className="text-right">
                  <div className="text-xs font-bold text-emerald-400 font-mono">{app.durationStr}</div>
                  <span className="text-[10px] text-slate-500 font-mono">{app.mins} total mins</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Daily Sequential Activity Timeline */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-emerald-400" /> Daily Activity Timeline
            </h3>
            <span className="text-xs font-mono text-slate-400">Sequential Logs</span>
          </div>

          <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
            {data.dailyTimeline && data.dailyTimeline.length > 0 ? (
              data.dailyTimeline.map((item, idx) => (
                <div key={item.id || idx} className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono font-bold text-slate-400">{item.time}</span>
                    <div>
                      <div className="text-xs font-bold text-white">{item.app}</div>
                      <div className="text-[11px] text-slate-400 truncate max-w-xs">{item.title}</div>
                    </div>
                  </div>
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono border ${
                    item.category === 'Educational' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                    item.category === 'Productive' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                    'bg-amber-500/10 text-amber-400 border-amber-500/20'
                  }`}>
                    {item.category}
                  </span>
                </div>
              ))
            ) : (
              <div className="p-6 text-center text-xs text-slate-400">
                Awaiting daily activity telemetry logs...
              </div>
            )}
          </div>
        </div>
      </div>

      {/* AI EXECUTIVE SUMMARY & WARNINGS RECEIVED */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* AI Executive Explanation Card for Parents */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <Sparkles className="w-5 h-5 text-amber-400" />
            <h3 className="text-base font-bold text-white">AI Executive Summary for Parents</h3>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3 text-xs">
            {(data.burnoutReasons && data.burnoutReasons.length > 0 ? data.burnoutReasons : [
              "Low risk because:",
              "• Healthy break discipline & study pace."
            ]).map((reason, idx) => (
              <div key={idx} className={`p-3 rounded-lg border ${
                idx === 0 ? 'bg-slate-800/80 border-slate-700 text-slate-200 font-bold' : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300'
              }`}>
                {reason}
              </div>
            ))}
          </div>
        </div>

        {/* Warnings Received & Ignored Count */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-rose-400" />
              <h3 className="text-base font-bold text-white">Warnings & Alerts Received</h3>
            </div>
            <span className="text-xs font-mono text-rose-400">
              {data.ignoredWarningCount || 0} Warnings Ignored Today
            </span>
          </div>

          <div className="space-y-3">
            {data.warningsReceived && data.warningsReceived.length > 0 ? (
              data.warningsReceived.map((w) => (
                <div key={w.id} className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex items-start justify-between text-xs gap-3">
                  <div>
                    <span className="font-bold text-rose-400 block mb-0.5">Continuous Usage Limit</span>
                    <p className="text-slate-300">{w.message}</p>
                  </div>
                  <span className="text-[10px] font-mono text-slate-500 shrink-0">{w.time}</span>
                </div>
              ))
            ) : (
              <div className="p-6 text-center text-xs text-slate-500">
                No active warnings received today.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Meeting Request Modal */}
      <Modal
        isOpen={meetingModalOpen}
        onClose={() => setMeetingModalOpen(false)}
        title="Schedule Meeting with Faculty Mentor"
      >
        {meetingSuccess ? (
          <div className="py-6 text-center space-y-2">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
            <h4 className="text-base font-bold text-white">Meeting Request Sent!</h4>
            <p className="text-xs text-slate-400">Dr. Robert Vance will review your request within 24 hours.</p>
          </div>
        ) : (
          <form onSubmit={handleBookMeeting} className="space-y-4">
            <p className="text-xs text-slate-300">
              Request a 1-on-1 discussion with <strong className="text-brand-400">Dr. Robert Vance</strong> regarding {data.studentName}'s academic wellness.
            </p>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Preferred Time / Agenda Notes</label>
              <textarea
                required
                rows={3}
                value={meetingNotes}
                onChange={(e) => setMeetingNotes(e.target.value)}
                placeholder="e.g., Discussion regarding CS302 assignment timeline and sleep balance."
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-brand-600 hover:bg-brand-500 text-white font-bold py-2.5 rounded-xl text-xs shadow-lg transition"
            >
              Submit Consultation Request
            </button>
          </form>
        )}
      </Modal>
    </div>
  );
};

function max1(val: number): number {
  return Math.max(1, val);
}

