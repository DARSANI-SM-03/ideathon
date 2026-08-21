import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  Activity,
  GraduationCap,
  ShieldAlert,
  Radio,
  BarChart3,
  Users,
  Award
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';

  const studentLinks = [
    { to: '/student/dashboard', label: 'Overview', icon: LayoutDashboard },
    { to: '/student/activities', label: 'Activity Logs', icon: Activity },
    { to: '/student/academic', label: 'Academic Performance', icon: GraduationCap },
  ];

  const adminLinks = [
    { to: '/admin/dashboard', label: 'Executive Intelligence', icon: BarChart3 },
    { to: '/admin/high-risk', label: 'High-Risk Interventions', icon: ShieldAlert },
    { to: '/admin/monitoring', label: 'Live App Telemetry', icon: Radio },
  ];

  const currentLinks = isAdmin ? adminLinks : studentLinks;

  return (
    <aside className="w-64 glass-panel border-r border-slate-800/80 p-4 flex flex-col justify-between hidden md:flex min-h-[calc(100vh-4rem)]">
      <div className="space-y-6">
        <div>
          <div className="px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
            {isAdmin ? 'Administration Portal' : 'Student Intelligence'}
          </div>
          <nav className="space-y-1">
            {currentLinks.map((link) => {
              const Icon = link.icon;
              return (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition ${
                      isActive
                        ? 'bg-brand-600/15 text-brand-400 border border-brand-500/30 shadow-md shadow-brand-500/10'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                    }`
                  }
                >
                  <Icon className="w-4 h-4" />
                  {link.label}
                </NavLink>
              );
            })}
          </nav>
        </div>

        <div className="pt-4 border-t border-slate-800/60">
          <div className="px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
            System Modules
          </div>
          <div className="space-y-2 px-3 text-xs text-slate-400">
            <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/40 border border-slate-800/60">
              <span className="flex items-center gap-2">
                <Users className="w-3.5 h-3.5 text-brand-400" /> Parent Portal API
              </span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-mono">READY</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/40 border border-slate-800/60">
              <span className="flex items-center gap-2">
                <Award className="w-3.5 h-3.5 text-purple-400" /> Mentor Portal API
              </span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-mono">READY</span>
            </div>
          </div>
        </div>
      </div>

      <div className="glass-card p-4 rounded-xl border border-slate-800 text-center">
        <p className="text-xs font-semibold text-slate-300">Offline Autonomous AI</p>
        <p className="text-[11px] text-slate-500 mt-1">Focus & Burnout models executing locally.</p>
      </div>
    </aside>
  );
};
