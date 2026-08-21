import React from 'react';

export const Skeleton: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div className={`animate-pulse bg-slate-800/60 rounded-xl ${className}`} />
  );
};

export const CardSkeleton: React.FC = () => (
  <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-3">
    <Skeleton className="h-4 w-1/3" />
    <Skeleton className="h-8 w-2/3" />
    <Skeleton className="h-3 w-1/2" />
  </div>
);

export const DashboardSkeleton: React.FC = () => (
  <div className="space-y-6">
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {[...Array(4)].map((_, i) => <CardSkeleton key={i} />)}
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="glass-card p-5 rounded-2xl border border-slate-800 h-64">
        <Skeleton className="h-full w-full" />
      </div>
      <div className="glass-card p-5 rounded-2xl border border-slate-800 h-64">
        <Skeleton className="h-full w-full" />
      </div>
    </div>
  </div>
);

export const ListSkeleton: React.FC<{ rows?: number }> = ({ rows = 5 }) => (
  <div className="space-y-3">
    {[...Array(rows)].map((_, i) => (
      <div key={i} className="glass-card p-4 rounded-xl border border-slate-800 flex items-center gap-4">
        <Skeleton className="h-10 w-10 rounded-full shrink-0" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
        </div>
        <Skeleton className="h-6 w-16 rounded-full" />
      </div>
    ))}
  </div>
);

