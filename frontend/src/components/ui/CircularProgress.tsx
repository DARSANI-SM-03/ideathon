import React from 'react';

interface CircularProgressProps {
  value: number;
  size?: number;
  strokeWidth?: number;
  label?: string;
  sublabel?: string;
  type?: 'focus' | 'burnout';
}

export const CircularProgress: React.FC<CircularProgressProps> = ({
  value,
  size = 140,
  strokeWidth = 12,
  label,
  sublabel,
  type = 'focus'
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (value / 100) * circumference;

  let strokeColor = '#3b82f6';
  if (type === 'focus') {
    if (value >= 80) strokeColor = '#10b981'; // Green
    else if (value >= 50) strokeColor = '#f59e0b'; // Yellow
    else strokeColor = '#f43f5e'; // Red
  } else {
    if (value >= 75) strokeColor = '#f43f5e'; // Critical / High (Red)
    else if (value >= 50) strokeColor = '#f97316'; // High (Orange)
    else if (value >= 30) strokeColor = '#f59e0b'; // Medium (Yellow)
    else strokeColor = '#10b981'; // Low (Green)
  }

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background Track Circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-slate-800/80"
          fill="transparent"
        />
        {/* Foreground Progress Circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          fill="transparent"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        <span className="text-2xl font-extrabold text-slate-100 tracking-tight">{value}</span>
        {label && <span className="text-[11px] font-medium text-slate-400 font-mono mt-0.5">{label}</span>}
        {sublabel && <span className="text-[10px] text-slate-500 font-sans">{sublabel}</span>}
      </div>
    </div>
  );
};
