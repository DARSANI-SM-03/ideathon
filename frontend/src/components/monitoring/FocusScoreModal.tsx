import React from 'react';
import { Modal } from '../Modal';
import { Brain, CheckCircle, AlertTriangle, Zap, RefreshCw } from 'lucide-react';

interface FocusScoreModalProps {
  isOpen: boolean;
  onClose: () => void;
  focusScore: number;
  breakdown?: {
    educational_hours?: number;
    productive_hours?: number;
    entertainment_hours?: number;
    idle_mins?: number;
    app_switches_count?: number;
    positive_points?: number;
    distraction_penalty?: number;
    academic_ratio_pct?: number;
    formula_str?: string;
  };
}

export const FocusScoreModal: React.FC<FocusScoreModalProps> = ({
  isOpen,
  onClose,
  focusScore,
  breakdown
}) => {
  const eduHrs = breakdown?.educational_hours ?? 3.5;
  const prodHrs = breakdown?.productive_hours ?? 1.5;
  const entHrs = breakdown?.entertainment_hours ?? 0.8;
  const idleMins = breakdown?.idle_mins ?? 12.0;
  const switches = breakdown?.app_switches_count ?? 8;
  const formula = breakdown?.formula_str || 'Focus Score = Base (60) + (Academic Ratio * 0.3) + Positive Boost - Distraction Penalties';

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Dynamic Focus Score Calculation Engine">
      <div className="space-y-4 py-2 font-sans text-xs">
        <div className="p-4 rounded-2xl bg-slate-900 border border-brand-500/30 flex items-center justify-between">
          <div>
            <span className="text-[10px] uppercase font-mono text-brand-400 font-bold tracking-wider">Current Live Focus Score</span>
            <div className="text-3xl font-black text-white">{focusScore} <span className="text-sm font-normal text-slate-400">/ 100</span></div>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-brand-500/10 border border-brand-500/30 text-brand-400 flex items-center justify-center">
            <Brain className="w-6 h-6 animate-pulse" />
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-mono text-slate-300">
          <strong className="block text-brand-400 font-sans font-bold mb-1">Mathematical Formula:</strong>
          {formula}
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-slate-200">
            <span className="text-[10px] text-emerald-400 font-bold uppercase block mb-1 flex items-center gap-1">
              <CheckCircle className="w-3 h-3" /> Educational Time
            </span>
            <span className="text-base font-bold font-mono text-white">{eduHrs} hrs</span>
            <span className="text-[10px] text-slate-400 block mt-0.5">+ Positive Score Contribution</span>
          </div>

          <div className="p-3 rounded-xl bg-brand-500/10 border border-brand-500/20 text-slate-200">
            <span className="text-[10px] text-brand-400 font-bold uppercase block mb-1 flex items-center gap-1">
              <Zap className="w-3 h-3" /> Productive Time
            </span>
            <span className="text-base font-bold font-mono text-white">{prodHrs} hrs</span>
            <span className="text-[10px] text-slate-400 block mt-0.5">+ Positive Score Contribution</span>
          </div>

          <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-slate-200">
            <span className="text-[10px] text-amber-400 font-bold uppercase block mb-1 flex items-center gap-1">
              <AlertTriangle className="w-3 h-3" /> Entertainment Time
            </span>
            <span className="text-base font-bold font-mono text-white">{entHrs} hrs</span>
            <span className="text-[10px] text-slate-400 block mt-0.5">- Score Penalty Deduction</span>
          </div>

          <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-slate-200">
            <span className="text-[10px] text-rose-400 font-bold uppercase block mb-1 flex items-center gap-1">
              <RefreshCw className="w-3 h-3" /> App Switches & Idle
            </span>
            <span className="text-base font-bold font-mono text-white">{switches} switches ({idleMins}m idle)</span>
            <span className="text-[10px] text-slate-400 block mt-0.5">- Context Switching Penalty</span>
          </div>
        </div>

        <button
          onClick={onClose}
          className="w-full py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-bold transition shadow-lg mt-2"
        >
          Got It, Close Breakdown
        </button>
      </div>
    </Modal>
  );
};
