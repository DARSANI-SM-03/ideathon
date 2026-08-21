import React from 'react';
import { AcademicTrendChart } from '../../charts/AcademicTrendChart';
import { Badge } from '../../components/Badge';
import { GraduationCap, Award, BookOpen, CheckCircle } from 'lucide-react';

export const AcademicOverviewPage: React.FC = () => {
  const quizScores = [
    { subject: 'Algorithms & Data Structures', quiz: 'Quiz 2 - Trees & Graphs', score: 94, max: 100, date: '2026-07-28' },
    { subject: 'Machine Learning Systems', quiz: 'Midterm Evaluation', score: 88, max: 100, date: '2026-07-20' },
    { subject: 'Database Systems', quiz: 'SQL Optimization Test', score: 91, max: 100, date: '2026-07-15' },
    { subject: 'Computer Networks', quiz: 'Quiz 1 - TCP/IP Stack', score: 84, max: 100, date: '2026-07-10' }
  ];

  const assignments = [
    { subject: 'Algorithms & Data Structures', title: 'Dynamic Programming Set #3', due: '2026-08-04', status: 'Completed', grade: 'A' },
    { subject: 'Machine Learning Systems', title: 'Neural Net Pipeline Project', due: '2026-08-08', status: 'Pending', grade: '—' },
    { subject: 'Database Systems', title: 'Index Tuning Benchmark', due: '2026-08-12', status: 'Pending', grade: '—' }
  ];

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <GraduationCap className="w-6 h-6 text-brand-400" />
          Academic Records & Performance Overview
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Attendance records, quiz marks, assignment deadlines, and historical SGPA trend.
        </p>
      </div>

      {/* Trend Chart */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800">
        <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
          <Award className="w-5 h-5 text-emerald-400" />
          Academic Progress vs Focus Correlation
        </h3>
        <AcademicTrendChart />
      </div>

      {/* Quiz & Assignment Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quiz Marks */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-brand-400" />
            Recent Quiz & Exam Marks
          </h3>
          <div className="space-y-3">
            {quizScores.map((q, idx) => (
              <div key={idx} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
                <div>
                  <div className="text-sm font-semibold text-slate-200">{q.subject}</div>
                  <div className="text-xs text-slate-400">{q.quiz} • {q.date}</div>
                </div>
                <div className="text-right">
                  <div className="text-base font-bold text-emerald-400">{q.score} / {q.max}</div>
                  <Badge variant="success">Passed</Badge>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Assignments */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-purple-400" />
            Upcoming Assignments & Coursework
          </h3>
          <div className="space-y-3">
            {assignments.map((a, idx) => (
              <div key={idx} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
                <div>
                  <div className="text-sm font-semibold text-slate-200">{a.title}</div>
                  <div className="text-xs text-slate-400">{a.subject} • Due: {a.due}</div>
                </div>
                <div>
                  <Badge variant={a.status === 'Completed' ? 'success' : 'medium'}>
                    {a.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
