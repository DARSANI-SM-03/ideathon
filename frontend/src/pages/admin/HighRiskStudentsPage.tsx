import React, { useEffect, useState } from 'react';
import { ApiService } from '../../services/api';
import { HighRiskStudent } from '../../types';
import { Badge } from '../../components/Badge';
import { ShieldAlert, Mail, Phone, Filter } from 'lucide-react';
import { Modal } from '../../components/Modal';

export const HighRiskStudentsPage: React.FC = () => {
  const [students, setStudents] = useState<HighRiskStudent[]>([]);
  const [filterDept, setFilterDept] = useState<string>('All');
  const [selectedStudent, setSelectedStudent] = useState<HighRiskStudent | null>(null);

  useEffect(() => {
    ApiService.fetchAdminDashboard().then((res) => {
      setStudents(res.high_risk_students_list);
    });
  }, []);

  const filteredStudents = filterDept === 'All'
    ? students
    : students.filter(s => s.department === filterDept);

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-rose-400" />
            High-Risk Student Interventions
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Predictive early warning roster for academic counseling, workload adjustment, and mentor escalation.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-500" />
          <select
            value={filterDept}
            onChange={(e) => setFilterDept(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
          >
            <option value="All">All Departments</option>
            <option value="Computer Science">Computer Science</option>
            <option value="Electronics & Comm">Electronics & Comm</option>
            <option value="Mechanical Eng">Mechanical Eng</option>
            <option value="Electrical Eng">Electrical Eng</option>
            <option value="Civil Eng">Civil Eng</option>
          </select>
        </div>
      </div>

      <div className="glass-card rounded-2xl p-6 border border-slate-800">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 text-slate-400 font-semibold uppercase font-mono">
              <tr>
                <th className="py-3.5 px-4">Student ID</th>
                <th className="py-3.5 px-4">Full Name</th>
                <th className="py-3.5 px-4">Department & Sem</th>
                <th className="py-3.5 px-4">Focus Index</th>
                <th className="py-3.5 px-4">Burnout Risk</th>
                <th className="py-3.5 px-4">Attendance</th>
                <th className="py-3.5 px-4">CGPA</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filteredStudents.map((st) => (
                <tr key={st.id} className="hover:bg-slate-900/40 transition">
                  <td className="py-3.5 px-4 font-mono text-brand-400">{st.student_id}</td>
                  <td className="py-3.5 px-4 font-semibold text-slate-100">{st.name}</td>
                  <td className="py-3.5 px-4 text-slate-400">{st.department} (Sem {st.semester})</td>
                  <td className="py-3.5 px-4 font-bold text-brand-400">{st.focus_score}</td>
                  <td className="py-3.5 px-4 font-bold text-rose-400">{st.burnout_score}%</td>
                  <td className="py-3.5 px-4 font-mono">{st.attendance}%</td>
                  <td className="py-3.5 px-4 font-mono">{st.cgpa}</td>
                  <td className="py-3.5 px-4">
                    <Badge variant={st.burnout_score > 75 ? 'critical' : 'high'}>
                      {st.risk_level}
                    </Badge>
                  </td>
                  <td className="py-3.5 px-4">
                    <button
                      onClick={() => setSelectedStudent(st)}
                      className="bg-brand-600/20 hover:bg-brand-600/30 text-brand-300 border border-brand-500/30 px-3 py-1 rounded-lg font-medium text-[11px] transition"
                    >
                      Intervene
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <Modal
        isOpen={!!selectedStudent}
        onClose={() => setSelectedStudent(null)}
        title={`Escalate Intervention: ${selectedStudent?.name}`}
      >
        <div className="space-y-4 text-xs text-slate-300">
          <div className="p-3 bg-slate-900 rounded-xl border border-slate-800 space-y-1">
            <div><strong className="text-slate-200">Student ID:</strong> {selectedStudent?.student_id}</div>
            <div><strong className="text-slate-200">Department:</strong> {selectedStudent?.department}</div>
            <div><strong className="text-slate-200">Burnout Risk Level:</strong> <span className="text-rose-400 font-bold">{selectedStudent?.burnout_score}%</span></div>
            <div><strong className="text-slate-200">Attendance:</strong> {selectedStudent?.attendance}%</div>
          </div>

          <p className="text-slate-400">
            Escalating will automatically notify the assigned Academic Mentor and Parent, and generate an automated workload reduction suggestion.
          </p>

          <div className="flex gap-2">
            <button
              onClick={() => {
                alert(`Intervention notice dispatched to Mentor & Parent for ${selectedStudent?.name}`);
                setSelectedStudent(null);
              }}
              className="flex-1 bg-rose-600 hover:bg-rose-500 text-white font-medium py-2 rounded-xl flex items-center justify-center gap-1.5"
            >
              <Mail className="w-4 h-4" /> Notify Mentor & Parent
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
