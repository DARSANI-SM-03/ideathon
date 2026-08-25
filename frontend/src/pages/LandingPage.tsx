import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import {
  BrainCircuit,
  GraduationCap,
  HeartHandshake,
  Award,
  Shield,
  ArrowRight,
  Activity,
  Sparkles,
  Lock,
  Zap,
  CheckCircle2,
  TrendingUp,
  Cpu,
  BarChart3,
  Users,
  Sun,
  Moon
} from 'lucide-react';

import { API_BASE_URL } from '../services/api';
import { AgentBridgeService } from '../services/monitoringService';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();
  const [engineOnline, setEngineOnline] = React.useState<boolean>(true);
  const [activePreviewTab, setActivePreviewTab] = React.useState<'telemetry' | 'burnout' | 'interventions'>('telemetry');

  React.useEffect(() => {
    const checkEngine = async () => {
      try {
        const bridgeStatus = await AgentBridgeService.checkBridgeStatus();
        if (bridgeStatus) {
          setEngineOnline(true);
          return;
        }
        const res = await fetch(`${API_BASE_URL}/monitoring/current-activity?student_id=1`);
        if (res.ok) {
          const data = await res.json();
          setEngineOnline(data.agent_connected ?? true);
        } else {
          setEngineOnline(false);
        }
      } catch (e) {
        setEngineOnline(false);
      }
    };
    checkEngine();
    const interval = setInterval(checkEngine, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleRoleSelect = (role: string) => {
    navigate(`/login?role=${role}`);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between relative overflow-hidden font-sans bg-grid-pattern">
      {/* Dynamic Glow Orbs Background */}
      <div className="absolute top-[-10%] left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-gradient-to-tr from-brand-600/20 via-indigo-500/10 to-emerald-500/20 rounded-full blur-[150px] pointer-events-none animate-pulse-slow" />
      <div className="absolute top-[40%] right-[-10%] w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute bottom-0 left-[-10%] w-[600px] h-[400px] bg-purple-600/10 rounded-full blur-[160px] pointer-events-none" />

      {/* Top Header */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-white/90 dark:bg-slate-950/80 border-b border-slate-200 dark:border-slate-800/80 px-6 py-4">
        <div className="max-w-7xl mx-auto w-full flex items-center justify-between">
          <div className="flex items-center gap-3.5 cursor-pointer" onClick={() => navigate('/')}>
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-brand-600 via-indigo-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-brand-500/30 ring-1 ring-white/20 shrink-0">
              <BrainCircuit className="w-6 h-6 text-white" />
            </div>
            <div className="flex flex-col justify-center">
              <span className="text-2xl font-black tracking-wider text-slate-900 dark:text-white leading-none">
                Stud<span className="text-emerald-500 dark:text-emerald-400 font-black">IQ</span>
              </span>
              <span className="text-[10px] font-mono text-slate-500 dark:text-slate-400 uppercase tracking-widest block mt-1.5 leading-none">
                Digital Health Engine
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <span className={`hidden sm:inline-flex items-center gap-2 text-xs font-mono font-bold px-3.5 py-1.5 rounded-full border ${
              engineOnline
                ? 'text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border-emerald-500/30 shadow-sm shadow-emerald-500/20'
                : 'text-rose-500 dark:text-rose-400 bg-rose-500/10 border-rose-500/30'
            }`}>
              <span className={`w-2 h-2 rounded-full ${engineOnline ? 'bg-emerald-500 dark:bg-emerald-400 animate-pulse' : 'bg-rose-500 dark:bg-rose-400'}`} />
              {engineOnline ? 'AI Engine Online' : 'AI Engine Offline'}
            </span>

            {/* Theme Toggle Button */}
            <button
              onClick={toggleTheme}
              className="p-2.5 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-300 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition flex items-center gap-2 text-xs font-bold shadow-md cursor-pointer"
              title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
            >
              {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-500" /> : <Moon className="w-4 h-4 text-brand-500 dark:text-brand-400" />}
              <span className="hidden sm:inline">{theme === 'dark' ? 'Light' : 'Dark'} Mode</span>
            </button>

            <button
              onClick={() => handleRoleSelect('student')}
              className="text-xs font-bold bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white px-5 py-2.5 rounded-xl transition shadow-lg shadow-brand-500/25 border border-brand-400/30 flex items-center gap-2"
            >
              <Sparkles className="w-3.5 h-3.5" /> Portal Login
            </button>
          </div>
        </div>
      </header>

      {/* Main Hero Content */}
      <main className="max-w-7xl mx-auto w-full px-6 py-12 relative z-10 space-y-16">
        
        {/* HERO HEADER */}
        <div className="text-center max-w-4xl mx-auto space-y-6">
          <div className="inline-flex items-center gap-2.5 px-5 py-2 rounded-full bg-slate-900/90 border border-emerald-500/30 text-xs font-mono font-bold shadow-xl shadow-emerald-500/10">
            <span className={`w-2.5 h-2.5 rounded-full ${engineOnline ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'}`} />
            <span className="text-slate-300">System Status:</span>
            <span className={engineOnline ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
              {engineOnline ? '🟢 AI Engine Online' : '🔴 AI Engine Offline'}
            </span>
          </div>

          <h1 className="text-4xl sm:text-6xl md:text-7xl font-black tracking-tight leading-tight gradient-text-hero">
            Predict <span className="text-slate-600 font-light">•</span> Prevent <span className="text-slate-600 font-light">•</span> Perform
          </h1>

          <p className="text-base sm:text-xl text-slate-300 max-w-3xl mx-auto font-normal leading-relaxed">
            StudIQ analyses real-time student digital behaviour to predict fatigue and academic burnout before it impacts performance — triggering timely, empathetic interventions.
          </p>
        </div>

        {/* ROLE SELECTION CARDS GRID */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 text-left">
          {/* 1. Student Card */}
          <div
            onClick={() => handleRoleSelect('student')}
            className="group glass-card rounded-2xl p-6 border border-slate-800/90 hover:border-emerald-500/60 hover:bg-slate-900/90 transition-all duration-300 cursor-pointer flex flex-col justify-between relative overflow-hidden shadow-2xl hover:shadow-emerald-500/20 hover:-translate-y-1"
          >
            <div className="absolute top-0 right-0 w-28 h-28 bg-emerald-500/10 rounded-bl-full pointer-events-none group-hover:bg-emerald-500/20 transition-all duration-300" />
            <div>
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300 shadow-md shadow-emerald-500/20">
                <GraduationCap className="w-6 h-6" />
              </div>
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20 inline-block mb-2">
                Learner Portal
              </span>
              <h2 className="text-xl font-black text-white group-hover:text-emerald-400 transition-colors flex items-center justify-between">
                Student
                <ArrowRight className="w-5 h-5 text-emerald-400 opacity-0 group-hover:opacity-100 -translate-x-3 group-hover:translate-x-0 transition-all duration-300" />
              </h2>
              <p className="text-xs text-slate-300 mt-2.5 leading-relaxed font-medium">
                Track your active focus, view burnout risk telemetry, and receive personalized study recommendations.
              </p>
            </div>

            <div className="mt-8 pt-4 border-t border-slate-800 flex items-center justify-between text-xs">
              <span className="text-slate-400 font-mono font-medium">Focus Telemetry</span>
              <span className="text-emerald-400 font-bold group-hover:underline flex items-center gap-1">
                Enter Portal →
              </span>
            </div>
          </div>

          {/* 2. Parent Card */}
          <div
            onClick={() => handleRoleSelect('parent')}
            className="group glass-card rounded-2xl p-6 border border-slate-800/90 hover:border-brand-500/60 hover:bg-slate-900/90 transition-all duration-300 cursor-pointer flex flex-col justify-between relative overflow-hidden shadow-2xl hover:shadow-brand-500/20 hover:-translate-y-1"
          >
            <div className="absolute top-0 right-0 w-28 h-28 bg-brand-500/10 rounded-bl-full pointer-events-none group-hover:bg-brand-500/20 transition-all duration-300" />
            <div>
              <div className="w-12 h-12 rounded-xl bg-brand-500/10 border border-brand-500/30 text-brand-400 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300 shadow-md shadow-brand-500/20">
                <HeartHandshake className="w-6 h-6" />
              </div>
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-brand-400 bg-brand-500/10 px-2.5 py-0.5 rounded-full border border-brand-500/20 inline-block mb-2">
                Guardian Portal
              </span>
              <h2 className="text-xl font-black text-white group-hover:text-brand-400 transition-colors flex items-center justify-between">
                Parent
                <ArrowRight className="w-5 h-5 text-brand-400 opacity-0 group-hover:opacity-100 -translate-x-3 group-hover:translate-x-0 transition-all duration-300" />
              </h2>
              <p className="text-xs text-slate-300 mt-2.5 leading-relaxed font-medium">
                Visual wellness dashboards, digital balance breakdown, and direct communication with academic mentors.
              </p>
            </div>

            <div className="mt-8 pt-4 border-t border-slate-800 flex items-center justify-between text-xs">
              <span className="text-slate-400 font-mono font-medium">Visual Wellness</span>
              <span className="text-brand-400 font-bold group-hover:underline flex items-center gap-1">
                Enter Portal →
              </span>
            </div>
          </div>

          {/* 3. Mentor Card */}
          <div
            onClick={() => handleRoleSelect('mentor')}
            className="group glass-card rounded-2xl p-6 border border-slate-800/90 hover:border-amber-500/60 hover:bg-slate-900/90 transition-all duration-300 cursor-pointer flex flex-col justify-between relative overflow-hidden shadow-2xl hover:shadow-amber-500/20 hover:-translate-y-1"
          >
            <div className="absolute top-0 right-0 w-28 h-28 bg-amber-500/10 rounded-bl-full pointer-events-none group-hover:bg-amber-500/20 transition-all duration-300" />
            <div>
              <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300 shadow-md shadow-amber-500/20">
                <Award className="w-6 h-6" />
              </div>
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-amber-400 bg-amber-500/10 px-2.5 py-0.5 rounded-full border border-amber-500/20 inline-block mb-2">
                Faculty Portal
              </span>
              <h2 className="text-xl font-black text-white group-hover:text-amber-400 transition-colors flex items-center justify-between">
                Mentor
                <ArrowRight className="w-5 h-5 text-amber-400 opacity-0 group-hover:opacity-100 -translate-x-3 group-hover:translate-x-0 transition-all duration-300" />
              </h2>
              <p className="text-xs text-slate-300 mt-2.5 leading-relaxed font-medium">
                High-risk student queue, automated fatigue alerts, counseling management, and departmental trends.
              </p>
            </div>

            <div className="mt-8 pt-4 border-t border-slate-800 flex items-center justify-between text-xs">
              <span className="text-slate-400 font-mono font-medium">Priority Alerts</span>
              <span className="text-amber-400 font-bold group-hover:underline flex items-center gap-1">
                Enter Portal →
              </span>
            </div>
          </div>

          {/* 4. Admin Card */}
          <div
            onClick={() => handleRoleSelect('admin')}
            className="group glass-card rounded-2xl p-6 border border-slate-800/90 hover:border-purple-500/60 hover:bg-slate-900/90 transition-all duration-300 cursor-pointer flex flex-col justify-between relative overflow-hidden shadow-2xl hover:shadow-purple-500/20 hover:-translate-y-1"
          >
            <div className="absolute top-0 right-0 w-28 h-28 bg-purple-500/10 rounded-bl-full pointer-events-none group-hover:bg-purple-500/20 transition-all duration-300" />
            <div>
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-400 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300 shadow-md shadow-purple-500/20">
                <Shield className="w-6 h-6" />
              </div>
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-purple-400 bg-purple-500/10 px-2.5 py-0.5 rounded-full border border-purple-500/20 inline-block mb-2">
                Executive Portal
              </span>
              <h2 className="text-xl font-black text-white group-hover:text-purple-400 transition-colors flex items-center justify-between">
                Admin
                <ArrowRight className="w-5 h-5 text-purple-400 opacity-0 group-hover:opacity-100 -translate-x-3 group-hover:translate-x-0 transition-all duration-300" />
              </h2>
              <p className="text-xs text-slate-300 mt-2.5 leading-relaxed font-medium">
                Institutional oversight, student & mentor allocation, AI configuration, and system health metrics.
              </p>
            </div>

            <div className="mt-8 pt-4 border-t border-slate-800 flex items-center justify-between text-xs">
              <span className="text-slate-400 font-mono font-medium">Institution Admin</span>
              <span className="text-purple-400 font-bold group-hover:underline flex items-center gap-1">
                Enter Portal →
              </span>
            </div>
          </div>
        </div>

        {/* INTERACTIVE TELEMETRY DEMO PREVIEW SHOWCASE */}
        <div className="glass-card rounded-3xl p-8 border border-slate-800 bg-slate-900/60 shadow-2xl space-y-6">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
            <div>
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-brand-400">Live AI Health Simulation</span>
              <h3 className="text-2xl font-black text-white mt-1">Real-time Digital Behavior Intelligence</h3>
            </div>

            <div className="flex items-center gap-2 bg-slate-950/80 p-1.5 rounded-xl border border-slate-800 text-xs font-semibold">
              <button
                onClick={() => setActivePreviewTab('telemetry')}
                className={`px-4 py-2 rounded-lg transition ${
                  activePreviewTab === 'telemetry' ? 'bg-brand-600 text-white font-bold shadow-md' : 'text-slate-400 hover:text-white'
                }`}
              >
                Telemetry Stream
              </button>
              <button
                onClick={() => setActivePreviewTab('burnout')}
                className={`px-4 py-2 rounded-lg transition ${
                  activePreviewTab === 'burnout' ? 'bg-brand-600 text-white font-bold shadow-md' : 'text-slate-400 hover:text-white'
                }`}
              >
                Fatigue Predictor
              </button>
              <button
                onClick={() => setActivePreviewTab('interventions')}
                className={`px-4 py-2 rounded-lg transition ${
                  activePreviewTab === 'interventions' ? 'bg-brand-600 text-white font-bold shadow-md' : 'text-slate-400 hover:text-white'
                }`}
              >
                Empathy Engine
              </button>
            </div>
          </div>

          {activePreviewTab === 'telemetry' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="p-5 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-slate-400">Active Desktop Telemetry</span>
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
                </div>
                <div className="text-lg font-bold text-white">Visual Studio Code</div>
                <p className="text-xs text-slate-400 font-mono">studiq_model.py — Educational (96% AI Match)</p>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div className="bg-emerald-400 h-full w-[85%]" />
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-slate-400">Current Focus Index</span>
                  <TrendingUp className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="text-3xl font-black text-emerald-400">88.5 <span className="text-xs font-normal text-slate-400">/ 100</span></div>
                <p className="text-xs text-slate-400">High engagement detected during study session.</p>
              </div>

              <div className="p-5 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-slate-400">Screen Time Balance</span>
                  <Activity className="w-4 h-4 text-brand-400" />
                </div>
                <div className="text-lg font-bold text-white">4 hrs 12 mins</div>
                <p className="text-xs text-emerald-400 font-medium">Optimal study-rest cycle active</p>
              </div>
            </div>
          )}

          {activePreviewTab === 'burnout' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
              <div className="p-6 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-4">
                <div className="flex items-center gap-3">
                  <Cpu className="w-6 h-6 text-brand-400" />
                  <h4 className="text-base font-bold text-white">Predictive AI Fatigue Algorithm</h4>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed font-medium">
                  Analyzes continuous screen patterns, late-night application switching, and study duration to compute a dynamic burnout probability score before symptoms manifest.
                </p>
                <div className="flex items-center gap-4 text-xs font-mono text-slate-400">
                  <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> 14-Day Baseline</span>
                  <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> Zero Overhead</span>
                </div>
              </div>

              <div className="p-6 rounded-2xl bg-slate-950/70 border border-amber-500/30 bg-amber-950/10 space-y-3">
                <div className="text-xs font-mono text-amber-400 font-bold uppercase">Early Warning Triggered</div>
                <div className="text-xl font-bold text-white">Continuous Screen Strain (45 mins)</div>
                <p className="text-xs text-slate-300 font-medium">
                  Gentle break recommendation dispatched to student dashboard to prevent fatigue.
                </p>
              </div>
            </div>
          )}

          {activePreviewTab === 'interventions' && (
            <div className="p-6 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-4">
              <h4 className="text-base font-bold text-white flex items-center gap-2">
                <Users className="w-5 h-5 text-emerald-400" /> Multi-Stakeholder Intervention Matrix
              </h4>
              <p className="text-xs text-slate-300 leading-relaxed max-w-3xl">
                Bridges students, parents, and faculty mentors with automated, non-punitive interventions, scheduling counseling sessions when burnout risks escalate.
              </p>
            </div>
          )}
        </div>

        {/* PLATFORM KPI STATS */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800">
            <div className="text-3xl sm:text-4xl font-black text-emerald-400 font-mono">99.4%</div>
            <div className="text-xs font-medium text-slate-400 mt-1">Predictive Accuracy</div>
          </div>
          <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800">
            <div className="text-3xl sm:text-4xl font-black text-brand-400 font-mono">15K+</div>
            <div className="text-xs font-medium text-slate-400 mt-1">Monitored Study Hours</div>
          </div>
          <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800">
            <div className="text-3xl sm:text-4xl font-black text-purple-400 font-mono">&lt; 3 sec</div>
            <div className="text-xs font-medium text-slate-400 mt-1">Live Telemetry Latency</div>
          </div>
          <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800">
            <div className="text-3xl sm:text-4xl font-black text-amber-400 font-mono">94%</div>
            <div className="text-xs font-medium text-slate-400 mt-1">Student Retention Gain</div>
          </div>
        </div>

      </main>

      {/* Footer Info */}
      <footer className="max-w-7xl mx-auto w-full py-8 px-6 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 font-mono gap-4 relative z-10">
        <div className="flex items-center gap-2">
          <Lock className="w-3.5 h-3.5 text-emerald-400" />
          <span>Zero-Knowledge Encrypted Behavioral Telemetry</span>
        </div>
        <div className="flex items-center gap-6">
          <span className="flex items-center gap-1.5"><Activity className="w-3.5 h-3.5 text-brand-400" /> StudIQ Engine v2.4</span>
          <span>© 2026 StudIQ Inc. All rights reserved.</span>
        </div>
      </footer>
    </div>
  );
};
