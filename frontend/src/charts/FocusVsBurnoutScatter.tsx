import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface StudentPoint {
  student: string;
  focusScore: number;
  burnoutScore: number;
  risk?: string;
}

interface Props {
  students?: StudentPoint[];
}

export const FocusVsBurnoutScatter: React.FC<Props> = ({ students = [] }) => {
  const chartData = students.length > 0
    ? students
    : [
        { student: 'Alex Mercer', focusScore: 85, burnoutScore: 15, risk: 'Normal' },
        { student: 'Sophia Patel', focusScore: 48, burnoutScore: 74, risk: 'High Risk' },
        { student: 'Marcus Chen', focusScore: 35, burnoutScore: 88, risk: 'High Risk' }
      ];

  return (
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 10, right: 10, bottom: 10, left: -20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis type="number" dataKey="focusScore" name="Focus Score" unit="" stroke="#64748b" domain={[0, 100]} />
          <YAxis type="number" dataKey="burnoutScore" name="Burnout Risk" unit="%" stroke="#64748b" domain={[0, 100]} />
          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#f8fafc' }}
          />
          <Scatter name="Students" data={chartData} fill="#10b981" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};

