import React from 'react';
import { AlertTriangle, BookOpen, AlertOctagon } from 'lucide-react';
import { Modal } from '../Modal';

interface WarningModalProps {
  isOpen: boolean;
  ignoredCount: number;
  onContinueStudying: () => void;
  onIgnore: () => void;
}

export const WarningModal: React.FC<WarningModalProps> = ({
  isOpen,
  ignoredCount,
  onContinueStudying,
  onIgnore
}) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={() => {}}
      title="Healthy Digital Usage Warning"
    >
      <div className="space-y-4 py-2 font-sans">
        <div className="w-12 h-12 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center mx-auto">
          <AlertTriangle className="w-6 h-6" />
        </div>

        <div className="text-center space-y-1">
          <h3 className="text-base font-bold text-white">Entertainment Threshold Exceeded</h3>
          <p className="text-xs text-slate-300 max-w-sm mx-auto leading-relaxed">
            You have exceeded your healthy entertainment limit. Consider returning to your study session.
          </p>
        </div>

        <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-[11px] text-slate-400 font-mono text-center">
          Ignored Warnings: <strong className="text-amber-400">{ignoredCount} / 5</strong>
          {ignoredCount >= 4 && (
            <span className="block text-rose-400 font-sans text-[10px] mt-1 font-semibold">
              Warning: 6th ignored warning will lock this study session & notify parent.
            </span>
          )}
        </div>

        <div className="grid grid-cols-2 gap-3 pt-2">
          <button
            onClick={onContinueStudying}
            className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2.5 rounded-xl text-xs flex items-center justify-center gap-1.5 transition shadow-lg shadow-emerald-500/20"
          >
            <BookOpen className="w-4 h-4" /> Continue Studying
          </button>

          <button
            onClick={onIgnore}
            className="w-full bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold py-2.5 rounded-xl text-xs flex items-center justify-center gap-1.5 transition border border-slate-700"
          >
            <AlertOctagon className="w-4 h-4 text-slate-400" /> Ignore ({5 - ignoredCount} left)
          </button>
        </div>
      </div>
    </Modal>
  );
};
