import React from 'react';
import { useAuth } from '../context/AuthContext';
import { BrainCircuit, Bell, LogOut, Search, UserCheck } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 glass-panel sticky top-0 z-40 border-b border-slate-800/80 px-6 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-emerald-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
          <BrainCircuit className="w-6 h-6 text-white" />
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xl font-black font-sans tracking-wider text-white">
            Stud<span className="text-emerald-400 font-black">IQ</span>
          </span>
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
            AI Platform v1.0
          </span>
        </div>
      </div>

      <div className="hidden md:flex items-center gap-4 flex-1 max-w-md mx-8">
        <div className="relative w-full">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
          <input
            type="text"
            placeholder="Search student records, activity logs, or courses..."
            className="w-full bg-slate-900/90 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition"
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button className="p-2 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-900 transition relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        </button>

        <div className="h-6 w-px bg-slate-800" />

        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-sm font-bold text-brand-400">
            {user?.name.charAt(0) || 'U'}
          </div>
          <div className="hidden sm:block text-left">
            <div className="text-sm font-semibold text-slate-200 flex items-center gap-1.5">
              {user?.name}
              <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <div className="text-xs text-slate-400 capitalize font-mono">{user?.role} Mode</div>
          </div>

          <button
            onClick={logout}
            className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition ml-2"
            title="Logout"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  );
};
