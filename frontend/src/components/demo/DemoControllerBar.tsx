import React, { useState } from 'react';
import { Sparkles, Radio, AlertTriangle, ShieldCheck, RefreshCw } from 'lucide-react';
import { useToast } from '../../context/ToastContext';
import { ARCHETYPE_STUDENT_A, ARCHETYPE_STUDENT_B, ARCHETYPE_STUDENT_C, ARCHETYPE_STUDENT_D } from '../../services/mockData';

interface DemoControllerProps {
  onSelectArchetype?: (profile: any) => void;
}

export const DemoControllerBar: React.FC<DemoControllerProps> = ({ onSelectArchetype }) => {
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState<'A' | 'B' | 'C' | 'D'>('A');

  const handleSelect = (letter: 'A' | 'B' | 'C' | 'D', profile: any, name: string) => {
    setActiveTab(letter);
    if (onSelectArchetype) onSelectArchetype(profile);
    showToast(`Switched to Demo Archetype Profile: ${name}`, 'info');
  };

  const handleSimulateTelemetry = () => {
    showToast('Ingested Windows 11 Telemetry: VS Code (Educational Context)', 'success');
  };

  const handleSimulateWarning = () => {
    showToast('Warning Engine: Entertainment Limit Exceeded (95m / 90m limit)', 'warning');
  };

  const handleSimulateParentAlert = () => {
    showToast('Parent API Escalation Triggered: 5th Warning Ignored by Student', 'error');
  };

  return (
    <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 z-40 glass-card rounded-2xl px-5 py-3 border border-brand-500/40 shadow-2xl backdrop-blur-xl flex flex-wrap items-center justify-between gap-4 max-w-4xl w-[92%] animate-in fade-in slide-in-from-bottom duration-300">
      <div className="flex items-center gap-2">
        <div className="p-1.5 rounded-lg bg-brand-500/20 text-brand-400">
          <Sparkles className="w-4 h-4" />
        </div>
        <div>
          <span className="text-xs font-bold text-slate-100 block">Hackathon Live Demo Bar</span>
          <span className="text-[10px] text-slate-400 font-mono">Simulate AI & Telemetry Flow</span>
        </div>
      </div>

      {/* Archetype Profile Switcher Buttons */}
      <div className="flex items-center gap-1.5 bg-slate-900/90 p-1 rounded-xl border border-slate-800">
        <button
          onClick={() => handleSelect('A', ARCHETYPE_STUDENT_A, 'Alex Mercer (Student A)')}
          className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition ${
            activeTab === 'A' ? 'bg-emerald-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Student A (94 Focus)
        </button>
        <button
          onClick={() => handleSelect('B', ARCHETYPE_STUDENT_B, 'Sophia Smith (Student B)')}
          className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition ${
            activeTab === 'B' ? 'bg-brand-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Student B (74 Focus)
        </button>
        <button
          onClick={() => handleSelect('C', ARCHETYPE_STUDENT_C, 'David Miller (Student C)')}
          className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition ${
            activeTab === 'C' ? 'bg-amber-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Student C (78% Burnout)
        </button>
        <button
          onClick={() => handleSelect('D', ARCHETYPE_STUDENT_D, 'Ava Jackson (Student D)')}
          className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition ${
            activeTab === 'D' ? 'bg-rose-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Student D (88% Critical)
        </button>
      </div>

      {/* Action Trigger Buttons */}
      <div className="flex items-center gap-2">
        <button
          onClick={handleSimulateTelemetry}
          className="px-2.5 py-1 rounded-xl bg-slate-900 hover:bg-slate-800 text-emerald-400 border border-emerald-500/30 text-[11px] font-semibold flex items-center gap-1 transition"
        >
          <Radio className="w-3 h-3" /> Telemetry Ping
        </button>
        <button
          onClick={handleSimulateWarning}
          className="px-2.5 py-1 rounded-xl bg-slate-900 hover:bg-slate-800 text-amber-400 border border-amber-500/30 text-[11px] font-semibold flex items-center gap-1 transition"
        >
          <AlertTriangle className="w-3 h-3" /> Warning Popup
        </button>
        <button
          onClick={handleSimulateParentAlert}
          className="px-2.5 py-1 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/30 text-[11px] font-semibold flex items-center gap-1 transition"
        >
          <ShieldCheck className="w-3 h-3" /> Parent Escalation
        </button>
      </div>
    </div>
  );
};
