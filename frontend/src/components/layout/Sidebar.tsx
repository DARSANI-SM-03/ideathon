import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard,
  BarChart3,
  History,
  Lightbulb,
  FileText,
  Timer,
  Settings,
  Users,
  UserCheck,
  Award,
  HeartHandshake,
  Building,
  BrainCircuit,
  GraduationCap,
  Monitor,
  Shield,
  MessageSquare,
  Calendar,
  ShieldAlert,
  Radio
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const { user } = useAuth();
  const role = user?.role || 'student';

  const studentLinks = [
    { to: '/student/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/student/monitoring', label: 'Live Telemetry (Hero)', icon: Radio },
    { to: '/student/analytics', label: 'Focus Analytics', icon: BarChart3 },
    { to: '/student/history', label: 'Activity History', icon: History },
    { to: '/student/recommendations', label: 'AI Recommendations', icon: Lightbulb },
    { to: '/student/reports', label: 'Reports', icon: FileText },
    { to: '/student/timer', label: 'Focus Timer', icon: Timer },
    { to: '/student/settings', label: 'Settings', icon: Settings },
  ];

  const parentLinks = [
    { to: '/parent/dashboard', label: 'Dashboard Overview', icon: LayoutDashboard },
    { to: '/parent/academic', label: 'Academic Overview', icon: GraduationCap },
    { to: '/parent/digital-behavior', label: 'Digital Behavior', icon: Monitor },
    { to: '/parent/insights', label: 'AI Insights', icon: Lightbulb },
    { to: '/parent/controls', label: 'Parental Controls', icon: Shield },
    { to: '/parent/reports', label: 'Reports', icon: FileText },
    { to: '/parent/messages', label: 'Messages & Mentor', icon: MessageSquare },
  ];

  const mentorLinks = [
    { to: '/mentor/dashboard', label: 'Dashboard Hub', icon: LayoutDashboard },
    { to: '/mentor/priority-queue', label: 'High-Risk Priority Queue', icon: ShieldAlert },
    { to: '/mentor/students', label: 'Assigned Mentees', icon: Users },
    { to: '/mentor/counseling', label: 'Counseling Sessions', icon: Award },
    { to: '/mentor/meetings', label: 'Meetings', icon: Calendar },
    { to: '/mentor/messages', label: 'Messages', icon: MessageSquare },
    { to: '/mentor/reports', label: 'Mentorship Reports', icon: FileText },
  ];

  const adminLinks = [
    { to: '/admin/dashboard', label: 'Dashboard Overview', icon: LayoutDashboard },
    { to: '/admin/students', label: 'Students Directory', icon: Users },
    { to: '/admin/parents', label: 'Parents Directory', icon: HeartHandshake },
    { to: '/admin/mentors', label: 'Mentors Allocation', icon: Award },
    { to: '/admin/teachers', label: 'Teachers & Faculty', icon: UserCheck },
    { to: '/admin/departments', label: 'Departments Analytics', icon: Building },
    { to: '/admin/reports', label: 'Campus Reports', icon: FileText },
    { to: '/admin/settings', label: 'AI & System Settings', icon: Settings },
  ];

  let currentLinks = studentLinks;
  let portalTitle = 'STUDENT PORTAL';

  if (role === 'admin') {
    currentLinks = adminLinks;
    portalTitle = 'ADMINISTRATION PORTAL';
  } else if (role === 'parent') {
    currentLinks = parentLinks;
    portalTitle = 'PARENT GUARDIAN PORTAL';
  } else if (role === 'mentor') {
    currentLinks = mentorLinks;
    portalTitle = 'FACULTY MENTOR PORTAL';
  }

  return (
    <aside className="w-64 glass-panel border-r border-slate-800/80 p-4 flex flex-col justify-between hidden md:flex min-h-[calc(100vh-4rem)] font-sans">
      <div className="space-y-6">
        <div>
          <div className="px-3 text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-3 font-mono">
            {portalTitle}
          </div>
          <nav className="space-y-1">
            {currentLinks.map((link) => {
              const Icon = link.icon;
              return (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition ${
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
      </div>

      <div className="glass-card p-4 rounded-xl border border-slate-800/80 text-center">
        <div className="flex items-center justify-center gap-1.5 text-xs font-bold text-brand-400 mb-1">
          <BrainCircuit className="w-4 h-4 text-emerald-400" /> StudIQ Core v2.4
        </div>
        <p className="text-[11px] text-slate-400">Digital Behaviour Engine Active</p>
      </div>
    </aside>
  );
};
