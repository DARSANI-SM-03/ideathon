import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, BarChart, Bar,
} from 'recharts';
import type { WeeklyFocusPoint } from '@/types';

interface WeeklyFocusChartProps {
  data: WeeklyFocusPoint[];
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass-card border border-surface-border px-4 py-3 text-xs space-y-1 shadow-card">
        <p className="font-semibold text-white mb-2">{label}</p>
        {payload.map((entry: any) => (
          <div key={entry.name} className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full" style={{ background: entry.color }} />
            <span className="text-gray-400">{entry.name}:</span>
            <span className="text-white font-medium">{entry.value}{entry.name === 'Focus Score' ? '' : 'm'}</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export function WeeklyFocusChart({ data }: WeeklyFocusChartProps) {
  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="section-title">Weekly Focus Trend</h3>
          <p className="section-subtitle mt-0.5">This week's focus score and study time</p>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis dataKey="day" tick={{ fill: '#6b7280', fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: '#6b7280', fontSize: 12 }} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            formatter={(value) => <span style={{ color: '#9ca3af', fontSize: '12px' }}>{value}</span>}
          />
          <Line
            type="monotone"
            dataKey="focusScore"
            name="Focus Score"
            stroke="#6366f1"
            strokeWidth={2.5}
            dot={{ fill: '#6366f1', r: 4, strokeWidth: 0 }}
            activeDot={{ r: 6, fill: '#818cf8' }}
          />
          <Line
            type="monotone"
            dataKey="entertainmentTime"
            name="Entertainment (min)"
            stroke="#f43f5e"
            strokeWidth={2}
            dot={{ fill: '#f43f5e', r: 3, strokeWidth: 0 }}
            strokeDasharray="4 2"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function TimeBarChart({ data }: { data: WeeklyFocusPoint[] }) {
  return (
    <div className="glass-card p-5">
      <h3 className="section-title mb-4">Study vs Entertainment</h3>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis dataKey="day" tick={{ fill: '#6b7280', fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: '#6b7280', fontSize: 12 }} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Legend formatter={(v) => <span style={{ color: '#9ca3af', fontSize: '12px' }}>{v}</span>} />
          <Bar dataKey="productiveTime" name="Study (min)" fill="#6366f1" radius={[4, 4, 0, 0]} />
          <Bar dataKey="entertainmentTime" name="Entertainment (min)" fill="#f43f5e" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
