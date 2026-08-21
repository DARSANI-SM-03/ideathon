import React from 'react';
import { FileText, Download } from 'lucide-react';
import { useToast } from '../../context/ToastContext';
import { exportReportPDF } from '../../utils/pdfExport';

export const ParentReportsPage: React.FC = () => {
  const { showToast } = useToast();

  const handleDownloadPDF = (reportType: string, title: string) => {
    showToast(`Generating ${title} PDF Report...`, 'success');
    exportReportPDF(reportType);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Parental Intelligence Reports</h1>
        <p className="text-xs text-slate-400 mt-1">Download consolidated weekly and semester academic performance audits</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-card p-6 rounded-2xl border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-brand-400 font-mono">WEEKLY AUDIT</span>
            <h3 className="text-sm font-bold text-white mt-1">July Week 4 - Behavioral Summary</h3>
            <p className="text-xs text-slate-400 mt-1">Focus Score: 84% | Attendance: 92.5%</p>
          </div>
          <button
            onClick={() => handleDownloadPDF('weekly', 'July Week 4 Behavioral Summary')}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold transition cursor-pointer active:scale-95 shadow-lg shadow-brand-600/20"
          >
            <Download className="w-4 h-4" /> Download PDF
          </button>
        </div>

        <div className="glass-card p-6 rounded-2xl border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-emerald-400 font-mono">SEMESTER AUDIT</span>
            <h3 className="text-sm font-bold text-white mt-1">Semester 4 Mid-Term Progress</h3>
            <p className="text-xs text-slate-400 mt-1">CGPA: 3.82 | Credit Completion: 100%</p>
          </div>
          <button
            onClick={() => handleDownloadPDF('semester', 'Semester 4 Mid-Term Progress')}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold transition cursor-pointer active:scale-95 shadow-lg shadow-brand-600/20"
          >
            <Download className="w-4 h-4 text-white" /> Download PDF
          </button>
        </div>
      </div>
    </div>
  );
};

