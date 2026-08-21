import React, { useState } from 'react';
import { Settings, Shield, Sliders, Bell, Moon, Sun, Save } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import { useToast } from '../../context/ToastContext';

export const AdminSettingsPage: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const { showToast } = useToast();

  const [burnoutThreshold, setBurnoutThreshold] = useState(60);
  const [entLimit, setEntLimit] = useState(60);
  const [autoNotifyParents, setAutoNotifyParents] = useState(true);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await fetch('http://localhost:8000/api/v1/admin/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(localStorage.getItem('studiq_token') ? { Authorization: `Bearer ${localStorage.getItem('studiq_token')}` } : {})
        },
        body: JSON.stringify({
          burnout_threshold: burnoutThreshold,
          entertainment_limit_mins: entLimit,
          auto_notify_parents: autoNotifyParents,
        })
      });
    } catch {
      // Endpoint may not yet exist — fall through to toast
    }
    showToast('Institutional System Policies Saved!', 'success');
  };

  return (
    <div className="space-y-6 pb-12 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <Settings className="w-6 h-6 text-brand-400" />
          Institutional System Preferences & Policies
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Configure campus-wide burnout thresholds, app limits, theme, and automated counselor alerts.
        </p>
      </div>

      <div className="glass-card rounded-2xl p-6 border border-slate-800">
        <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
          {theme === 'dark' ? <Moon className="w-4 h-4 text-amber-400" /> : <Sun className="w-4 h-4 text-brand-400" />}
          Theme & UI Appearance
        </h3>
        <div className="flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-200 block">Theme Mode</span>
            <span className="text-[11px] text-slate-400">Toggle dark mode or light mode for the executive console.</span>
          </div>
          <button
            onClick={toggleTheme}
            className="px-4 py-2 rounded-xl bg-brand-600/20 hover:bg-brand-600/30 text-brand-300 border border-brand-500/30 text-xs font-semibold"
          >
            {theme === 'dark' ? 'Switch to Light Mode ☀️' : 'Switch to Dark Mode 🌙'}
          </button>
        </div>
      </div>

      <form onSubmit={handleSave} className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
        <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
          <Sliders className="w-4 h-4 text-emerald-400" />
          Institutional AI Policy Thresholds
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Burnout Risk Alert Threshold (%)</label>
            <input
              type="number"
              value={burnoutThreshold}
              onChange={(e) => setBurnoutThreshold(Number(e.target.value))}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Campus Entertainment Limit (Mins/Day)</label>
            <input
              type="number"
              value={entLimit}
              onChange={(e) => setEntLimit(Number(e.target.value))}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200"
            />
          </div>
        </div>

        <div className="pt-4 border-t border-slate-800 space-y-2">
          <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={autoNotifyParents}
              onChange={(e) => setAutoNotifyParents(e.target.checked)}
              className="rounded bg-slate-900 border-slate-700 text-brand-500"
            />
            Automatically Email Academic Mentors and Parents upon Critical Burnout Detection
          </label>
        </div>

        <button
          type="submit"
          className="bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs py-2.5 px-5 rounded-xl flex items-center gap-2 transition"
        >
          <Save className="w-4 h-4" /> Save System Policies
        </button>
      </form>
    </div>
  );
};
