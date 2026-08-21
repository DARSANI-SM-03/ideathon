import React from 'react';
import { FocusTimer } from '../../components/ui/FocusTimer';
import { Timer } from 'lucide-react';

export const FocusTimerPage: React.FC = () => {
  return (
    <div className="space-y-6 pb-12 max-w-4xl mx-auto">
      <div className="text-center">
        <h1 className="text-3xl font-extrabold text-slate-100 flex items-center justify-center gap-2">
          <Timer className="w-8 h-8 text-brand-400" />
          Pomodoro Focus Workspace
        </h1>
        <p className="text-sm text-slate-400 mt-2">
          Deep work study timer with automated 50-minute focus blocks and 10-minute breaks.
        </p>
      </div>

      <div className="py-6">
        <FocusTimer />
      </div>
    </div>
  );
};
