import React from 'react';
import { Modal } from '../Modal';
import { Flame, Clock, Moon, AlertOctagon, Gamepad2, Tv, ShieldAlert } from 'lucide-react';

interface BurnoutScoreModalProps {
  isOpen: boolean;
  onClose: () => void;
  burnoutScore: number;
  burnoutLevel?: string;
  breakdown?: {
    continuous_usage_hours?: number;
    late_night_hours?: number;
    daily_study_hours?: number;
    breaks_count?: number;
    entertainment_hours?: number;
    gaming_hours?: number;
    factors?: string[];
  };
}

export const BurnoutScoreModal: React.FC<BurnoutScoreModalProps> = ({
  isOpen,
  onClose,
  burnoutScore,
  burnoutLevel = 'Low',
  breakdown
}) => {
  const continuousHrs = breakdown?.continuous_usage_hours ?? 1.8;
  const lateNightHrs = breakdown?.late_night_hours ?? 0.5;
  const dailyHrs = breakdown?.daily_study_hours ?? 4.2;
  const breaks = breakdown?.breaks_count ?? 3;
  const entHrs = breakdown?.entertainment_hours ?? 0.8;
  const gameHrs = breakdown?.gaming_hours ?? 0.3;
  const factors = breakdown?.factors || ['Balanced study pace & break frequency.'];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Burnout Risk Prediction Factor Breakdown">
      <div className="space-y-4 py-2 font-sans text-xs">
        <div className="p-4 rounded-2xl bg-slate-900 border border-rose-500/30 flex items-center justify-between">
          <div>
            <span className="text-[10px] uppercase font-mono text-rose-400 font-bold tracking-wider">Predicted Burnout Risk</span>
            <div className="text-3xl font-black text-white">{burnoutScore}% <span className="text-xs px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-400 font-bold border border-rose-500/30 ml-2">{burnoutLevel} Risk</span></div>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-400 flex items-center justify-center">
            <Flame className="w-6 h-6 animate-bounce text-rose-500" />
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
          <strong className="block text-slate-200 font-bold text-xs flex items-center gap-1.5">
            <ShieldAlert className="w-4 h-4 text-amber-400" /> Detected Contributing Risk Factors:
          </strong>
          <ul className="space-y-1 text-[11px] text-slate-300 font-mono pl-1">
            {factors.map((factor, idx) => (
              <li key={idx} className="flex items-start gap-1.5">
                <span className="text-rose-400 font-bold">•</span>
                <span>{factor}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-200">
            <span className="text-[10px] text-amber-400 font-bold uppercase block mb-1 flex items-center gap-1">
              <Clock className="w-3 h-3" /> Continuous Session
            </span>
            <span className="text-base font-bold font-mono text-white">{continuousHrs} hrs max</span>
            <span className="text-[10px] text-slate-400 block mt-0.5">Uninterrupted study length</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-200">
            <span className="text-[10px] text-purple-400 font-bold uppercase block mb-1 flex items-center gap-1">
              <Moon className="w-3 h-3" /> Late Night Activity
            </span>
            <span className="text-base font-bold font-mono text-white">{lateNightHrs} hrs</span>
            <span className="text-[10px] text-slate-400 block mt-0.5">Past 11:00 PM usage</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-200">
            <span className="text-[10px] text-emerald-400 font-bold uppercase block mb-1 flex items-center gap-1">
              <AlertOctagon className="w-3 h-3" /> Daily Breaks Count
            </span>
            <span className="text-base font-bold font-mono text-white">{breaks} breaks logged</span>
            <span className="text-[10px] text-slate-400 block mt-0.5">Study interval breaks</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-200">
            <span className="text-[10px] text-rose-400 font-bold uppercase block mb-1 flex items-center gap-1">
              <Gamepad2 className="w-3 h-3" /> Media & Gaming
            </span>
            <span className="text-base font-bold font-mono text-white">{entHrs}h ent / {gameHrs}h gaming</span>
            <span className="text-[10px] text-slate-400 block mt-0.5">High dopamine screen fatigue</span>
          </div>
        </div>

        <button
          onClick={onClose}
          className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold transition border border-slate-700 mt-2"
        >
          Close Risk Factor Analysis
        </button>
      </div>
    </Modal>
  );
};
