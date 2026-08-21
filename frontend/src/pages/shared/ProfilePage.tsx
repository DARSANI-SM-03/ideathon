import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { User, Mail, Shield, Building, GraduationCap, Award, HeartHandshake } from 'lucide-react';
import { Badge } from '../../components/Badge';

export const ProfilePage: React.FC = () => {
  const { user } = useAuth();

  const roleIcons = {
    student: <GraduationCap className="w-6 h-6 text-brand-400" />,
    admin: <Shield className="w-6 h-6 text-rose-400" />,
    teacher: <User className="w-6 h-6 text-emerald-400" />,
    mentor: <Award className="w-6 h-6 text-purple-400" />,
    parent: <HeartHandshake className="w-6 h-6 text-amber-400" />,
  };

  return (
    <div className="space-y-6 pb-12 max-w-4xl mx-auto">
      <div className="glass-card rounded-2xl p-6 border border-slate-800 flex items-center gap-5">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600 to-emerald-500 flex items-center justify-center text-2xl font-black text-white shadow-xl">
          {user?.name.charAt(0) || 'U'}
        </div>
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-slate-100">{user?.name}</h1>
            <Badge variant="info">{user?.role.toUpperCase()}</Badge>
          </div>
          <p className="text-xs text-slate-400 mt-1 flex items-center gap-2">
            <Mail className="w-3.5 h-3.5" /> {user?.email} • ID: <span className="font-mono text-brand-400">{user?.user_identifier}</span>
          </p>
        </div>
      </div>

      <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
        <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
          {roleIcons[user?.role || 'student']}
          Account Profile Information
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800">
            <span className="text-slate-500 block font-mono">ACCOUNT TYPE</span>
            <strong className="text-slate-200 text-sm capitalize">{user?.role} Portal Access</strong>
          </div>

          <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800">
            <span className="text-slate-500 block font-mono">DEPARTMENT / UNIT</span>
            <strong className="text-slate-200 text-sm">{user?.department || 'Computer Science'}</strong>
          </div>

          <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800">
            <span className="text-slate-500 block font-mono">ENCRYPTION & SECURITY</span>
            <strong className="text-emerald-400 text-sm">2FA & SHA-256 Authentication</strong>
          </div>

          <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800">
            <span className="text-slate-500 block font-mono">ACCOUNT STATUS</span>
            <strong className="text-emerald-400 text-sm">Verified Active Account</strong>
          </div>
        </div>
      </div>
    </div>
  );
};
