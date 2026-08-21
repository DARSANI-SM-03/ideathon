import { getStatusConfig } from '../../utils/helpers';
import type { StudentStatusType } from '../../types';
import { cn } from '../../utils/helpers';

interface StatusBadgeProps {
  status: StudentStatusType | string;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export function StatusBadge({ status, size = 'md', showLabel = true, className }: StatusBadgeProps) {
  const config = getStatusConfig(status as string);

  const dotSize = { sm: 'h-2 w-2', md: 'h-3 w-3', lg: 'h-4 w-4' }[size];
  const textSize = { sm: 'text-xs', md: 'text-sm', lg: 'text-base' }[size];

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className="relative">
        <div className={cn(dotSize, 'rounded-full', config.textClass || 'bg-emerald-400')} />
        <div
          className={cn(
            dotSize,
            'rounded-full absolute inset-0 animate-ping opacity-60',
            config.textClass || 'bg-emerald-400'
          )}
        />
      </div>
      {showLabel && (
        <span className={cn(textSize, 'font-medium', config.textClass || 'text-emerald-400')}>
          {config.label}
        </span>
      )}
    </div>
  );
}

interface StatusCardProps {
  status: StudentStatusType | string;
  currentApp: string;
  currentCategory: string;
  lastSyncTime: string;
}

export function StatusCard({ status, currentApp, currentCategory, lastSyncTime }: StatusCardProps) {
  const config = getStatusConfig(status as string);
  return (
    <div className={cn(
      'glass-card p-4 border border-slate-800',
      status === 'STUDYING' && 'border-emerald-500/30 bg-emerald-500/5',
      status === 'ENTERTAINMENT' && 'border-rose-500/30 bg-rose-500/5',
      status === 'HEALTHY_BREAK' && 'border-amber-500/30 bg-amber-500/5',
      status === 'PRODUCTIVE' && 'border-orange-500/30 bg-orange-500/5',
      status === 'OFFLINE' && 'border-gray-500/30',
    )}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div>
            <p className="text-xs text-slate-400 mb-0.5">Current Status</p>
            <div className="flex items-center gap-2">
              <StatusBadge status={status} size="md" />
            </div>
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs text-slate-500">Active App</p>
          <p className="text-sm font-semibold text-white">{currentApp}</p>
          <p className="text-xs text-slate-400">{currentCategory}</p>
        </div>
      </div>
      <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500 font-mono">
        <span>Last sync</span>
        <span>{lastSyncTime ? new Date(lastSyncTime).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : 'Just now'}</span>
      </div>
    </div>
  );
}
