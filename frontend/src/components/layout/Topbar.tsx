import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  BrainCircuit,
  Bell,
  Search,
  Sun,
  Moon,
  LogOut,
  User,
  Settings,
  ChevronRight,
  ShieldCheck,
  X,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';

export const Topbar: React.FC = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();

  const [profileOpen, setProfileOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);

  // Generate breadcrumbs from pathname
  const pathSegments = location.pathname.split('/').filter(Boolean);

  const notifications = [
    { id: 1, title: 'Weekly Focus Digest', text: 'AI Focus score increased by 12% this week.', time: '10m ago', type: 'info' },
    { id: 2, title: 'Late Night Activity Warning', text: 'Continuous IDE logs detected after 1 AM.', time: '2h ago', type: 'warning' },
    { id: 3, title: 'Assignment Due Reminder', text: 'CS302 ML Pipeline due in 24 hours.', time: '5h ago', type: 'info' }
  ];

  return (
    <header className="h-16 glass-panel sticky top-0 z-40 border-b border-slate-800/80 px-6 flex items-center justify-between">
      {/* Brand & Breadcrumbs */}
      <div className="flex items-center gap-4">
        <div
          onClick={() => navigate(user?.role === 'admin' ? '/admin/dashboard' : '/student/dashboard')}
          className="flex items-center gap-2 cursor-pointer"
        >
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-emerald-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
            <BrainCircuit className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-black font-sans tracking-wider text-white hidden sm:inline">
            Stud<span className="text-emerald-400 font-black">IQ</span>
          </span>
        </div>

        <div className="h-4 w-px bg-slate-800 hidden md:block" />

        {/* Breadcrumb Navigation */}
        <nav className="hidden md:flex items-center gap-1.5 text-xs text-slate-400 capitalize">
          <span className="hover:text-slate-200 cursor-pointer" onClick={() => navigate('/')}>Home</span>
          {pathSegments.map((segment, index) => (
            <React.Fragment key={index}>
              <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
              <span
                onClick={() => navigate(`/${pathSegments.slice(0, index + 1).join('/')}`)}
                className={`cursor-pointer ${
                  index === pathSegments.length - 1 ? 'font-semibold text-brand-400' : 'hover:text-slate-200'
                }`}
              >
                {segment.replace('-', ' ')}
              </span>
            </React.Fragment>
          ))}
        </nav>
      </div>

      {/* Center Search Bar */}
      <div className="hidden lg:flex items-center gap-4 flex-1 max-w-sm mx-6">
        <div className="relative w-full">
          <Search className="w-4 h-4 absolute left-3.5 top-2.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search students, courses, apps, or goals..."
            className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition"
          />
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-900 transition"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-brand-400" />}
        </button>

        {/* Notification Bell */}
        <div className="relative">
          <button
            onClick={() => setNotifOpen(!notifOpen)}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-900 transition relative"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          </button>

          {/* Notification Drawer Popover */}
          {notifOpen && (
            <div className="absolute right-0 mt-3 w-80 glass-card rounded-2xl p-4 border border-slate-800 shadow-2xl z-50 animate-in fade-in zoom-in-95 duration-150">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <span className="text-xs font-bold text-slate-100 uppercase tracking-wider">System Notifications</span>
                <button onClick={() => setNotifOpen(false)} className="text-slate-400 hover:text-slate-200">
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-2 mt-3 max-h-64 overflow-y-auto">
                {notifications.map((n) => (
                  <div key={n.id} className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800/80 text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                        {n.type === 'warning' ? <AlertTriangle className="w-3.5 h-3.5 text-amber-400" /> : <CheckCircle2 className="w-3.5 h-3.5 text-brand-400" />}
                        {n.title}
                      </span>
                      <span className="text-[10px] text-slate-500 font-mono">{n.time}</span>
                    </div>
                    <p className="text-[11px] text-slate-400">{n.text}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="h-5 w-px bg-slate-800" />

        {/* User Profile Dropdown */}
        <div className="relative">
          <button
            onClick={() => setProfileOpen(!profileOpen)}
            className="flex items-center gap-2 p-1.5 rounded-xl hover:bg-slate-900 transition border border-transparent hover:border-slate-800"
          >
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-brand-600 to-emerald-500 flex items-center justify-center text-xs font-bold text-white shadow-md">
              {user?.name.charAt(0) || 'U'}
            </div>
            <div className="hidden md:block text-left">
              <div className="text-xs font-semibold text-slate-200">{user?.name}</div>
              <div className="text-[10px] text-slate-400 capitalize font-mono">{user?.role}</div>
            </div>
          </button>

          {profileOpen && (
            <div className="absolute right-0 mt-3 w-56 glass-card rounded-2xl p-2 border border-slate-800 shadow-2xl z-50 animate-in fade-in zoom-in-95 duration-150">
              <div className="px-3 py-2 border-b border-slate-800 mb-1">
                <div className="text-xs font-bold text-slate-100">{user?.name}</div>
                <div className="text-[11px] text-slate-400">{user?.email}</div>
              </div>

              <button
                onClick={() => {
                  setProfileOpen(false);
                  navigate(user?.role === 'admin' ? '/admin/settings' : '/student/settings');
                }}
                className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-medium text-slate-300 hover:bg-slate-900 transition"
              >
                <User className="w-4 h-4 text-brand-400" /> Profile Settings
              </button>

              <button
                onClick={() => {
                  setProfileOpen(false);
                  logout();
                  navigate('/login');
                }}
                className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-medium text-rose-400 hover:bg-rose-500/10 transition"
              >
                <LogOut className="w-4 h-4" /> Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
