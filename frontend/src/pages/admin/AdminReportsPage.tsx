import React from 'react';
import { FileText, Download, Building, Users, Flame, Activity } from 'lucide-react';
import { useToast } from '../../context/ToastContext';
import { exportReportPDF, exportReportCSV } from '../../utils/pdfExport';

export const AdminReportsPage: React.FC = () => {
  const { showToast } = useToast();

  const reports = [
    { title: 'Institution Executive Summary', category: 'Institution Reports', desc: 'Overall enrollment, focus metrics, and burnout predictive health.', format: 'PDF & CSV' },
    { title: 'Department Comparison Audit', category: 'Department Reports', desc: 'Comparative analysis across CS, ECE, ME, EE, and Civil departments.', format: 'PDF & CSV' },
    { title: 'Campus Attendance Compliance', category: 'Attendance Reports', desc: 'Detailed attendance records and threshold breach warnings.', format: 'PDF & CSV' },
    { title: 'High Burnout Risk Intervention Roster', category: 'Burnout Reports', desc: 'List of students exceeding burnout risk threshold for counseling.', format: 'PDF & CSV' },
    { title: 'Digital Productivity & App Usage', category: 'Productivity Reports', desc: 'Aggregated application usage, window title classification, and study hours.', format: 'PDF & CSV' },
  ];

  const handleExport = (title: string, format: string) => {
    showToast(`Exporting ${title} in ${format} format...`, 'success');
    if (format === 'PDF') {
      exportReportPDF(title);
    } else {
      exportReportCSV(title);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <FileText className="w-6 h-6 text-brand-400" />
          Institutional Reports Generator & Export Center
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Generate downloadable PDF and CSV reports for Institution, Department, Attendance, Burnout, and Productivity audits.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {reports.map((r, idx) => (
          <div key={idx} className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-bold font-mono text-emerald-400 uppercase tracking-wider block mb-2">
                {r.category}
              </span>
              <h3 className="text-base font-bold text-slate-100 mb-2">{r.title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">{r.desc}</p>
            </div>

            <div className="flex gap-2 pt-4 border-t border-slate-800">
              <button
                onClick={() => handleExport(r.title, 'PDF')}
                className="flex-1 bg-brand-600/20 hover:bg-brand-600/30 text-brand-300 border border-brand-500/30 font-semibold text-xs py-2 rounded-xl flex items-center justify-center gap-1.5 transition"
              >
                <Download className="w-3.5 h-3.5" /> PDF
              </button>
              <button
                onClick={() => handleExport(r.title, 'CSV')}
                className="flex-1 bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 font-semibold text-xs py-2 rounded-xl flex items-center justify-center gap-1.5 transition"
              >
                <Download className="w-3.5 h-3.5" /> CSV
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
