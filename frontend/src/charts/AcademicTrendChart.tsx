import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export const AcademicTrendChart: React.FC = () => {
  const data = [
    { week: 'Wk 1', quiz: 82, attendance: 95, focus: 85 },
    { week: 'Wk 2', quiz: 85, attendance: 96, focus: 88 },
    { week: 'Wk 3', quiz: 78, attendance: 92, focus: 79 },
    { week: 'Wk 4', quiz: 88, attendance: 94, focus: 90 },
    { week: 'Wk 5', quiz: 92, attendance: 98, focus: 92 },
    { week: 'Wk 6', quiz: 89, attendance: 94, focus: 86 },
  ];

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="week" stroke="#64748b" tick={{ fontSize: 12 }} />
          <YAxis domain={[60, 100]} stroke="#64748b" tick={{ fontSize: 12 }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#f8fafc' }}
          />
          <Line type="monotone" dataKey="quiz" name="Quiz Score %" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4 }} />
          <Line type="monotone" dataKey="attendance" name="Attendance %" stroke="#10b981" strokeWidth={2} strokeDasharray="4 4" />
          <Line type="monotone" dataKey="focus" name="AI Focus Score" stroke="#8b5cf6" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
