import React, { useState } from 'react';
import { Settings, Bell, Shield, Moon, Sun } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

export const ParentSettingsPage: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [pushAlerts, setPushAlerts] = useState(true);

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Parental Portal Settings</h1>
        <p className="text-xs text-slate-400 mt-1">Configure notification preferences, security options, and reporting intervals</p>
      </div>

      <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-6">
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

        <div>
          <h2 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
            <Bell className="w-4 h-4 text-brand-400" /> Alert Subscriptions
          </h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3.5 rounded-xl glass-panel border border-slate-800">
              <div>
                <p className="text-xs font-semibold text-white">Email Digest & Alerts</p>
                <p className="text-[10px] text-slate-400">Receive weekly summaries and instant burnout alerts via email</p>
              </div>
              <input type="checkbox" checked={emailAlerts} onChange={(e) => setEmailAlerts(e.target.checked)} className="accent-brand-500 w-4 h-4 cursor-pointer" />
            </div>

            <div className="flex items-center justify-between p-3.5 rounded-xl glass-panel border border-slate-800">
              <div>
                <p className="text-xs font-semibold text-white">Real-Time Push Notifications</p>
                <p className="text-[10px] text-slate-400">Instant browser notifications when entertainment cap is exceeded</p>
              </div>
              <input type="checkbox" checked={pushAlerts} onChange={(e) => setPushAlerts(e.target.checked)} className="accent-brand-500 w-4 h-4 cursor-pointer" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

