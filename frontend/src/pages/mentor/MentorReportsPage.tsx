import React from 'react';
import { FileText, Download } from 'lucide-react';
import { useToast } from '../../context/ToastContext';
import { exportReportPDF } from '../../utils/pdfExport';

export const MentorReportsPage: React.FC = () => {
  const { showToast } = useToast();

  const handleDownloadPDF = (type: string, title: string) => {
    showToast(`Generating ${title} PDF Report...`, 'success');
    exportReportPDF(type);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Mentorship & Cohort Reports</h1>
        <p className="text-xs text-slate-400 mt-1">Export aggregated cohort analytics, risk logs, and counseling summaries</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-card p-6 rounded-2xl border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-brand-400 font-mono">COHORT DIGEST</span>
            <h3 className="text-sm font-bold text-white mt-1">July 2026 Cohort Risk Audit</h3>
            <p className="text-xs text-slate-400 mt-1">15 Students Monitored | 2 Interventions Pending</p>
          </div>
          <button
            onClick={() => handleDownloadPDF('cohort', 'July 2026 Cohort Risk Audit')}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold transition cursor-pointer active:scale-95 shadow-lg shadow-brand-600/20"
          >
            <Download className="w-4 h-4" /> Download PDF
          </button>
        </div>
      </div>
    </div>
  );
};

