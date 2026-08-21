import { cn } from '@/utils/helpers';
import type { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  iconColor?: string;
  iconBg?: string;
  trend?: {
    value: number;
    label?: string;
  };
  footer?: string;
  highlight?: boolean;
  className?: string;
  onClick?: () => void;
}

export function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  iconColor = 'text-brand-400',
  iconBg = 'bg-brand-500/15',
  trend,
  footer,
  highlight,
  className,
  onClick,
}: MetricCardProps) {
  return (
    <div
      className={cn(
        'metric-card cursor-default',
        highlight && 'border-brand-500/30 glow-purple',
        onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-3">
        <div className={cn('p-2.5 rounded-xl', iconBg)}>
          <Icon className={cn('h-5 w-5', iconColor)} />
        </div>
        {trend && (
          <span
            className={cn(
              'text-xs font-semibold px-2 py-1 rounded-lg',
              trend.value > 0
                ? 'text-emerald-400 bg-emerald-500/10'
                : 'text-rose-400 bg-rose-500/10'
            )}
          >
            {trend.value > 0 ? '↑' : '↓'} {Math.abs(trend.value)}%
          </span>
        )}
      </div>

      <p className="text-xs text-gray-500 font-medium mb-1 uppercase tracking-wide">{title}</p>
      <p className="text-2xl font-display font-bold text-white">{value}</p>

      {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
      {footer && (
        <p className="text-xs text-gray-500 mt-3 pt-3 border-t border-white/5">{footer}</p>
      )}
    </div>
  );
}

interface ProgressCardProps {
  title: string;
  value: number; // 0–100
  label?: string;
  color?: 'brand' | 'emerald' | 'amber' | 'rose';
  className?: string;
}

export function ProgressCard({ title, value, label, color = 'brand', className }: ProgressCardProps) {
  const colorMap = {
    brand: { text: 'text-brand-400', bar: 'bg-brand-500' },
    emerald: { text: 'text-emerald-400', bar: 'bg-emerald-500' },
    amber: { text: 'text-amber-400', bar: 'bg-amber-500' },
    rose: { text: 'text-rose-400', bar: 'bg-rose-500' },
  };
  const c = colorMap[color];

  return (
    <div className={cn('glass-card p-4', className)}>
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm text-gray-400">{title}</p>
        <span className={cn('text-lg font-bold font-display', c.text)}>{value}%</span>
      </div>
      <div className="h-2 bg-surface-muted rounded-full overflow-hidden">
        <div
          className={cn('h-full rounded-full transition-all duration-700', c.bar)}
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
      {label && <p className="text-xs text-gray-500 mt-2">{label}</p>}
    </div>
  );
}
