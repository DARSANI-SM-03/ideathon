import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

interface GaugeProps {
  focusScore: number;
  burnoutScore: number;
}

export const FocusBurnoutGauge: React.FC<GaugeProps> = ({ focusScore, burnoutScore }) => {
  const focusData = [
    { name: 'Focus', value: focusScore, color: '#3b82f6' },
    { name: 'Remaining', value: 100 - focusScore, color: '#1e293b' }
  ];

  const burnoutData = [
    { name: 'Burnout Risk', value: burnoutScore, color: burnoutScore > 60 ? '#f43f5e' : burnoutScore > 40 ? '#f59e0b' : '#10b981' },
    { name: 'Safety', value: 100 - burnoutScore, color: '#1e293b' }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Focus Score Gauge */}
      <div className="flex flex-col items-center justify-center p-4 bg-slate-900/60 rounded-xl border border-slate-800">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">AI Focus Index</span>
        <div className="w-full h-36 relative flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={focusData}
                cx="50%"
                cy="80%"
                startAngle={180}
                endAngle={0}
                innerRadius={55}
                outerRadius={75}
                paddingAngle={0}
                dataKey="value"
              >
                {focusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute top-[55%] left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
            <span className="text-3xl font-extrabold text-brand-400">{focusScore}</span>
            <span className="text-xs text-slate-500 block font-mono">/ 100</span>
          </div>
        </div>
        <span className="text-xs font-medium text-emerald-400 mt-[-10px] bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
          Optimal Flow State
        </span>
      </div>

      {/* Burnout Risk Gauge */}
      <div className="flex flex-col items-center justify-center p-4 bg-slate-900/60 rounded-xl border border-slate-800">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Burnout Risk Engine</span>
        <div className="w-full h-36 relative flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={burnoutData}
                cx="50%"
                cy="80%"
                startAngle={180}
                endAngle={0}
                innerRadius={55}
                outerRadius={75}
                paddingAngle={0}
                dataKey="value"
              >
                {burnoutData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute top-[55%] left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
            <span className={`text-3xl font-extrabold ${burnoutScore > 60 ? 'text-rose-400' : 'text-emerald-400'}`}>
              {burnoutScore}%
            </span>
            <span className="text-xs text-slate-500 block font-mono">Fatigue Risk</span>
          </div>
        </div>
        <span className={`text-xs font-medium mt-[-10px] px-2 py-0.5 rounded border ${
          burnoutScore > 60
            ? 'text-rose-400 bg-rose-500/10 border-rose-500/20'
            : 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
        }`}>
          {burnoutScore > 60 ? 'High Burnout Alert' : 'Low Fatigue Level'}
        </span>
      </div>
    </div>
  );
};
