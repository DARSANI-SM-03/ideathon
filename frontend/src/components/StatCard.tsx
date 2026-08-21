import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  variant?: 'blue' | 'emerald' | 'rose' | 'amber' | 'purple';
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  variant = 'blue'
}) => {
  const colorMap = {
    blue: 'border-brand-500/30 text-brand-400 bg-brand-500/10 glow-brand',
    emerald: 'border-emerald-500/30 text-emerald-400 bg-emerald-500/10 glow-emerald',
    rose: 'border-rose-500/30 text-rose-400 bg-rose-500/10 glow-rose',
    amber: 'border-amber-500/30 text-amber-400 bg-amber-500/10',
    purple: 'border-purple-500/30 text-purple-400 bg-purple-500/10',
  };

  return (
    <div className="glass-card rounded-2xl p-6 transition-all duration-300 hover:border-slate-700/80 hover:translate-y-[-2px]">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium text-slate-400">{title}</span>
        <div className={`p-3 rounded-xl border ${colorMap[variant]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="flex items-baseline justify-between">
        <h3 className="text-3xl font-bold text-slate-100 tracking-tight">{value}</h3>
        {trend && (
          <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
            trend.isPositive ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/15 text-rose-400 border border-rose-500/20'
          }`}>
            {trend.value}
          </span>
        )}
      </div>
      {subtitle && <p className="text-xs text-slate-400 mt-2">{subtitle}</p>}
    </div>
  );
};
