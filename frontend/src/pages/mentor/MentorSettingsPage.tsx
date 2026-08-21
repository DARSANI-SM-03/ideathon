import React, { useState } from 'react';
import { Settings, Bell, Shield, Moon, Sun } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

export const MentorSettingsPage: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [digestMode, setDigestMode] = useState(true);

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Mentor Portal Settings</h1>
        <p className="text-xs text-slate-400 mt-1">Configure weekly digest schedules and alert thresholds</p>
      </div>

      <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
        {/* Theme & Appearance */}
        <div>
          <h2 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
            {theme === 'dark' ? <Moon className="w-4 h-4 text-amber-400" /> : <Sun className="w-4 h-4 text-brand-400" />}
            Theme & UI Appearance
          </h2>
          <div className="flex items-center justify-between p-3.5 rounded-xl glass-panel border border-slate-800">
            <div>
              <span className="text-xs font-semibold text-slate-200 block">Current Theme Mode</span>
              <span className="text-[10px] text-slate-400">Toggle between Dark Mode 🌙 and High-Contrast Light Mode ☀️</span>
            </div>
            <button
              onClick={toggleTheme}
              className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold transition shadow-lg cursor-pointer"
            >
              {theme === 'dark' ? 'Switch to Light Mode ☀️' : 'Switch to Dark Mode 🌙'}
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between p-4 rounded-xl glass-panel border border-slate-800">
          <div>
            <h3 className="text-xs font-bold text-white">Weekly Intelligence Digest Mode</h3>
            <p className="text-[10px] text-slate-400">Consolidate mentee alerts into weekly high-level executive digests</p>
          </div>
          <input type="checkbox" checked={digestMode} onChange={(e) => setDigestMode(e.target.checked)} className="accent-brand-500 w-4 h-4 cursor-pointer" />
        </div>
      </div>
    </div>
  );
};

