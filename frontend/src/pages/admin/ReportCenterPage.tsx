import React, { useState } from 'react';
import { PDFReportTemplate } from '../../components/reports/PDFReportTemplate';
import { FileText, Printer, ArrowLeft } from 'lucide-react';

export const ReportCenterPage: React.FC = () => {
  const [selectedReport, setSelectedReport] = useState<string | null>(null);

  const reportTypes = [
    { title: 'Student Weekly Intelligence Report', category: 'Student' },
    { title: 'Student Monthly Intelligence Report', category: 'Student' },
    { title: 'Student Semester Performance Report', category: 'Student' },
    { title: 'Parent Portal Intelligence Summary', category: 'Parent' },
    { title: 'Mentor Weekly Digest Report', category: 'Mentor' },
    { title: 'Institution Executive Overview', category: 'Institution' },
    { title: 'Department Comparison Audit', category: 'Department' },
    { title: 'Burnout Risk Diagnostic Report', category: 'Burnout' },
    { title: 'AI Focus Index Report', category: 'Focus' },
    { title: 'Digital Productivity & App Usage Report', category: 'Productivity' },
    { title: 'Campus Attendance Compliance Report', category: 'Attendance' },
    { title: 'Assignment & Coursework Completion Report', category: 'Assignment' },
  ];

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <FileText className="w-6 h-6 text-brand-400" />
          StudIQ Report Center & PDF Engine
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Generate, preview, and print 12 specialized PDF report formats for Students, Parents, Mentors, and Administrators.
        </p>
      </div>

      {selectedReport ? (
        <div className="space-y-4">
          <button
            onClick={() => setSelectedReport(null)}
            className="bg-slate-900 border border-slate-800 text-slate-300 px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Report Center Roster
          </button>

          <PDFReportTemplate
            type={selectedReport}
            onPrint={() => window.print()}
          />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reportTypes.map((r, idx) => (
            <div
              key={idx}
              className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col justify-between hover:border-slate-700 transition"
            >
              <div>
                <span className="text-[10px] font-bold font-mono text-emerald-400 uppercase tracking-wider block mb-2">
                  {r.category} REPORT
                </span>
                <h3 className="text-sm font-bold text-slate-100 mb-4">{r.title}</h3>
              </div>

              <button
                onClick={() => setSelectedReport(r.title)}
                className="w-full bg-brand-600/20 hover:bg-brand-600/30 text-brand-300 border border-brand-500/30 font-semibold text-xs py-2 rounded-xl flex items-center justify-center gap-2 transition"
              >
                <Printer className="w-3.5 h-3.5" /> Preview & Export PDF
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
