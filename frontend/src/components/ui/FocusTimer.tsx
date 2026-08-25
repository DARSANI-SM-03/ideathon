import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, Sliders, Timer as TimerIcon } from 'lucide-react';
import { useToast } from '../../context/ToastContext';

import { ApiService } from '../../services/api';

export const FocusTimer: React.FC = () => {
  const { showToast } = useToast();
  const [studyMinutes, setStudyMinutes] = useState(50);
  const [breakMinutes, setBreakMinutes] = useState(10);
  const [mode, setMode] = useState<'study' | 'break'>('study');
  
  const [timeLeft, setTimeLeft] = useState(50 * 60);
  const [isRunning, setIsRunning] = useState(false);
  const [showCustomModal, setShowCustomModal] = useState(false);
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);

  useEffect(() => {
    let timer: any = null;
    if (isRunning && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (timeLeft === 0 && isRunning) {
      setIsRunning(false);
      if (mode === 'study') {
        showToast('Study Session Complete! Logged to Activity History.', 'success');
        if (activeSessionId) {
          ApiService.post(`/students/sessions/${activeSessionId}`, { completed: true, actual_duration_secs: studyMinutes * 60 }).catch(() => {});
        }
        setMode('break');
        setTimeLeft(breakMinutes * 60);
      } else {
        showToast('Break Complete! Ready for another study block.', 'info');
        setMode('study');
        setTimeLeft(studyMinutes * 60);
      }
    }
    return () => clearInterval(timer);
  }, [isRunning, timeLeft, mode, studyMinutes, breakMinutes, showToast, activeSessionId]);

  const toggleTimer = async () => {
    if (!isRunning && mode === 'study') {
      try {
        const res = await ApiService.post('/students/sessions', {
          session_type: 'Pomodoro',
          planned_duration_mins: studyMinutes
        });
        if (res && res.session_id) {
          setActiveSessionId(res.session_id);
        }
      } catch {}
    }
    setIsRunning(!isRunning);
  };

  const resetTimer = () => {
    setIsRunning(false);
    setTimeLeft((mode === 'study' ? studyMinutes : breakMinutes) * 60);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleCustomSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsRunning(false);
    setTimeLeft(studyMinutes * 60);
    setMode('study');
    setShowCustomModal(false);
    showToast(`Pomodoro updated: ${studyMinutes}m Study / ${breakMinutes}m Break`, 'info');
  };

  return (
    <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col items-center justify-between text-center relative overflow-hidden">
      {/* Background Mode Glow */}
      <div className={`absolute -top-10 -right-10 w-40 h-40 rounded-full blur-3xl ${
        mode === 'study' ? 'bg-brand-500/15' : 'bg-emerald-500/15'
      }`} />

      <div className="flex items-center justify-between w-full mb-4">
        <div className="flex items-center gap-2">
          <TimerIcon className="w-5 h-5 text-brand-400" />
          <span className="text-sm font-bold text-slate-100 uppercase tracking-wider">Pomodoro Focus Timer</span>
        </div>
        <button
          onClick={() => setShowCustomModal(true)}
          className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 transition text-xs flex items-center gap-1.5"
        >
          <Sliders className="w-3.5 h-3.5" /> Custom
        </button>
      </div>

      <div className="my-4">
        <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider border mb-3 ${
          mode === 'study'
            ? 'bg-brand-500/10 text-brand-400 border-brand-500/30'
            : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
        }`}>
          {mode === 'study' ? '🧠 Study Session (50 Min)' : '☕ Healthy Break (10 Min)'}
        </span>
        <div className="text-5xl md:text-6xl font-black font-mono tracking-tight text-slate-100">
          {formatTime(timeLeft)}
        </div>
      </div>

      <div className="flex items-center gap-3 mt-4">
        <button
          onClick={toggleTimer}
          className={`px-6 py-2.5 rounded-xl font-semibold text-xs flex items-center gap-2 transition shadow-lg ${
            isRunning
              ? 'bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30'
              : 'bg-gradient-to-r from-brand-600 to-emerald-600 hover:from-brand-500 hover:to-emerald-500 text-white shadow-brand-500/20'
          }`}
        >
          {isRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          {isRunning ? 'Pause' : 'Start Focus'}
        </button>

        <button
          onClick={resetTimer}
          className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 transition"
          title="Reset Timer"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* Custom Timer Modal */}
      {showCustomModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="glass-card rounded-2xl max-w-sm w-full p-6 text-left border border-slate-800">
            <h3 className="text-base font-bold text-slate-100 mb-4">Set Custom Timer Durations</h3>
            <form onSubmit={handleCustomSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Study Duration (Minutes)</label>
                <input
                  type="number"
                  min="5"
                  max="120"
                  value={studyMinutes}
                  onChange={(e) => setStudyMinutes(Number(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Break Duration (Minutes)</label>
                <input
                  type="number"
                  min="1"
                  max="45"
                  value={breakMinutes}
                  onChange={(e) => setBreakMinutes(Number(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200"
                />
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCustomModal(false)}
                  className="flex-1 bg-slate-900 border border-slate-800 text-slate-400 py-2 rounded-xl text-xs font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-brand-600 text-white py-2 rounded-xl text-xs font-semibold"
                >
                  Apply Custom Timer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
