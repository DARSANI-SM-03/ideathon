import React from 'react';
import { BrainCircuit, CheckCircle2, AlertTriangle, Calendar, Award, GraduationCap, Clock } from 'lucide-react';

interface ReportProps {
  type: string;
  studentName?: string;
  studentId?: string;
  department?: string;
  semester?: number;
  focusScore?: number;
  burnoutScore?: number;
  attendance?: number;
  cgpa?: number;
  avgQuiz?: number;
  productiveTimeMins?: number;
  entertainmentTimeMins?: number;
  onPrint?: () => void;
}

export const PDFReportTemplate: React.FC<ReportProps> = ({
  type = 'Weekly Intelligence Report',
  studentName = 'Alex Mercer',
  studentId = 'STU-2026-001',
  department = 'Computer Science',
  semester = 6,
  focusScore = 86.4,
  burnoutScore = 22.5,
  attendance = 94.2,
  cgpa = 3.84,
  avgQuiz = 89.5,
  productiveTimeMins = 285,
  entertainmentTimeMins = 42,
  onPrint
}) => {
  return (
    <div className="bg-slate-900 text-slate-100 p-8 rounded-2xl border border-slate-800 space-y-6 max-w-4xl mx-auto shadow-2xl print:bg-white print:text-black print:p-0">
      {/* Header with Institution Logo Placeholder */}
      <div className="flex items-center justify-between pb-6 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-brand-600 to-emerald-500 flex items-center justify-center shadow-lg">
            <BrainCircuit className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold font-sans tracking-wide">StudIQ Academic Intelligence Platform</h1>
            <p className="text-xs text-slate-400 font-mono">Digital Behavior & Academic Intelligence System</p>
          </div>
        </div>

        <div className="text-right">
          <span className="text-xs font-mono text-brand-400 font-bold block uppercase">{type}</span>
          <span className="text-[11px] text-slate-500 font-mono">Date Generated: 2026-07-31</span>
        </div>
      </div>

      {/* Student Details Card */}
      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
        <div>
          <span className="text-slate-500 block font-mono">STUDENT NAME</span>
          <strong className="text-slate-200 text-sm">{studentName}</strong>
        </div>
        <div>
          <span className="text-slate-500 block font-mono">STUDENT ID</span>
          <strong className="text-brand-400 text-sm font-mono">{studentId}</strong>
        </div>
        <div>
          <span className="text-slate-500 block font-mono">DEPARTMENT</span>
          <strong className="text-slate-200">{department}</strong>
        </div>
        <div>
          <span className="text-slate-500 block font-mono">SEMESTER / CGPA</span>
          <strong className="text-emerald-400">Sem {semester} • {cgpa} CGPA</strong>
        </div>
      </div>

      {/* Academic & AI Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
        <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-mono uppercase block mb-1">AI Focus Score</span>
          <span className="text-2xl font-black text-emerald-400">{focusScore}</span>
          <span className="text-[10px] text-slate-500 block mt-1 font-mono">/ 100 Index</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-mono uppercase block mb-1">Burnout Risk</span>
          <span className="text-2xl font-black text-brand-400">{burnoutScore}%</span>
          <span className="text-[10px] text-emerald-400 block mt-1 font-semibold">Low Fatigue Risk</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-mono uppercase block mb-1">Attendance Rate</span>
          <span className="text-2xl font-black text-purple-400">{attendance}%</span>
          <span className="text-[10px] text-slate-500 block mt-1 font-mono">Target &gt;85%</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-mono uppercase block mb-1">Quiz Average</span>
          <span className="text-2xl font-black text-amber-400">{avgQuiz}%</span>
          <span className="text-[10px] text-slate-500 block mt-1 font-mono">Class Rank: Top 5%</span>
        </div>
      </div>

      {/* AI Natural-Language Weekly Summary */}
      <div className="p-5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
        <h3 className="text-xs font-bold text-slate-200 uppercase font-mono tracking-wider flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          AI Natural-Language Weekly Intelligence Summary
        </h3>
        <div className="text-xs text-slate-300 space-y-1.5 leading-relaxed">
          <p>• You maintained excellent study consistency throughout the evaluation period.</p>
          <p>• Entertainment usage reduced by <strong className="text-emerald-400">22%</strong> compared to previous week baseline.</p>
          <p>• Assignment completion improved with 100% of coursework submitted on time.</p>
          <p>• Focus Score increased from 82.0 to <strong className="text-brand-400">91.0</strong>.</p>
          <p>• Burnout Risk decreased from Medium to <strong className="text-emerald-400">Low Fatigue Level</strong>.</p>
        </div>
      </div>

      {/* Daily AI Activity Timeline Sample */}
      <div className="p-5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-3">
        <h3 className="text-xs font-bold text-slate-200 uppercase font-mono tracking-wider">
          AI Activity Timeline Sample
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
          <div className="p-2 rounded bg-slate-900 border border-slate-800 flex justify-between">
            <span className="font-mono text-slate-400">09:00 - 10:30</span>
            <span className="font-semibold text-slate-200">VS Code (Educational)</span>
          </div>
          <div className="p-2 rounded bg-slate-900 border border-slate-800 flex justify-between">
            <span className="font-mono text-slate-400">10:30 - 11:15</span>
            <span className="font-semibold text-slate-200">YouTube ML Lecture (Educational)</span>
          </div>
          <div className="p-2 rounded bg-slate-900 border border-slate-800 flex justify-between">
            <span className="font-mono text-slate-400">11:15 - 11:45</span>
            <span className="font-semibold text-amber-400">Instagram (Entertainment)</span>
          </div>
          <div className="p-2 rounded bg-slate-900 border border-slate-800 flex justify-between">
            <span className="font-mono text-slate-400">11:45 - 13:00</span>
            <span className="font-semibold text-emerald-400">Returned to Study (Educational)</span>
          </div>
        </div>
      </div>

      {/* Professional Footer */}
      <div className="pt-6 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-500 font-mono">
        <span>Report Certified by StudIQ Autonomous Engine • Confidential Academic Document</span>
        {onPrint && (
          <button
            onClick={onPrint}
            className="bg-brand-600 hover:bg-brand-500 text-white font-semibold px-4 py-1.5 rounded-lg text-xs print:hidden"
          >
            Download / Print PDF
          </button>
        )}
      </div>
    </div>
  );
};
