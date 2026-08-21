import React from 'react';
import { FileText, Download, Calendar, CheckCircle } from 'lucide-react';
import { useToast } from '../../context/ToastContext';
import { exportReportPDF } from '../../utils/pdfExport';

export const ReportsPage: React.FC = () => {
  const { showToast } = useToast();

  const handleDownloadPDF = (type: string) => {
    showToast(`Generating and Downloading ${type} PDF Report...`, 'success');
    exportReportPDF(type);
  };

  const reports = [
    { type: 'Weekly', period: 'July 25 - July 31, 2026', focusAvg: '86.4 Index', burnoutRisk: 'Low (22.5%)', status: 'Generated' },
    { type: 'Monthly', period: 'July 01 - July 31, 2026', focusAvg: '84.1 Index', burnoutRisk: 'Low (24.0%)', status: 'Generated' },
    { type: 'Semester', period: 'Semester 6 (Spring 2026)', focusAvg: '85.8 Index', burnoutRisk: 'Healthy Baseline', status: 'Generated' },
  ];

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <FileText className="w-6 h-6 text-brand-400" />
          Academic Intelligence Reports
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Download PDF reports for Weekly, Monthly, and Semester academic performance and focus analytics.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {reports.map((r, idx) => (
          <div key={idx} className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-brand-400 font-mono">
                  {r.type} Intelligence Report
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
                  PDF READY
                </span>
              </div>

              <div className="text-sm font-semibold text-slate-200 mb-1">{r.period}</div>
              <div className="space-y-2 text-xs text-slate-400 my-4 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                <div className="flex justify-between">
                  <span>Avg Focus Score:</span>
                  <strong className="text-emerald-400">{r.focusAvg}</strong>
                </div>
                <div className="flex justify-between">
                  <span>Burnout Level:</span>
                  <strong className="text-slate-200">{r.burnoutRisk}</strong>
                </div>
              </div>
            </div>

            <button
              onClick={() => handleDownloadPDF(r.type)}
              className="w-full bg-gradient-to-r from-brand-600 to-emerald-600 hover:from-brand-500 hover:to-emerald-500 text-white font-semibold text-xs py-2.5 rounded-xl shadow-lg shadow-brand-500/20 flex items-center justify-center gap-2 transition"
            >
              <Download className="w-4 h-4" /> Export {r.type} Report (PDF)
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
