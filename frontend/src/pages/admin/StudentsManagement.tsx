import React, { useState } from 'react';
import { Search, Filter, Plus, Eye, Edit3, Key, Trash2, Users, ChevronLeft, ChevronRight } from 'lucide-react';
import { Badge } from '../../components/Badge';
import { Modal } from '../../components/Modal';
import { useToast } from '../../context/ToastContext';

export const StudentsManagement: React.FC = () => {
  const { showToast } = useToast();
  const [searchTerm, setSearchTerm] = useState('');
  const [deptFilter, setDeptFilter] = useState('All');
  const [currentPage, setCurrentPage] = useState(1);

  // Sample student dataset
  const [students, setStudents] = useState([
    { id: 1, student_id: 'STU-2026-001', name: 'Alex Mercer', email: 'alex.mercer@studiq.edu', department: 'Computer Science', semester: 6, cgpa: 3.84, focus: 86.4, burnout: 24.2, status: 'Active' },
    { id: 2, student_id: 'STU-2026-002', name: 'Sophia Smith', email: 'sophia.smith@studiq.edu', department: 'Electronics & Comm', semester: 4, cgpa: 3.65, focus: 78.0, burnout: 32.0, status: 'Active' },
    { id: 3, student_id: 'STU-2026-003', name: 'Liam Johnson', email: 'liam.j@studiq.edu', department: 'Computer Science', semester: 2, cgpa: 3.42, focus: 82.5, burnout: 28.0, status: 'Active' },
    { id: 4, student_id: 'STU-2026-004', name: 'Emma Williams', email: 'emma.w@studiq.edu', department: 'Mechanical Eng', semester: 8, cgpa: 3.90, focus: 91.0, burnout: 18.0, status: 'Active' },
    { id: 5, student_id: 'STU-2026-005', name: 'David Miller', email: 'david.m@studiq.edu', department: 'Electronics & Comm', semester: 4, cgpa: 2.85, focus: 42.1, burnout: 78.5, status: 'High Risk' },
    { id: 6, student_id: 'STU-2026-006', name: 'Ava Jackson', email: 'ava.j@studiq.edu', department: 'Civil Eng', semester: 8, cgpa: 2.70, focus: 39.5, burnout: 81.2, status: 'Critical' },
  ]);

  const [viewStudent, setViewStudent] = useState<any>(null);
  const [editStudent, setEditStudent] = useState<any>(null);
  const [resetPassStudent, setResetPassStudent] = useState<any>(null);
  const [newPassword, setNewPassword] = useState('');

  const filtered = students.filter((s) => {
    const matchesSearch = s.name.toLowerCase().includes(searchTerm.toLowerCase()) || s.student_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDept = deptFilter === 'All' || s.department === deptFilter;
    return matchesSearch && matchesDept;
  });

  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setStudents((prev) => prev.map((s) => (s.id === editStudent.id ? editStudent : s)));
    showToast(`Updated student profile for ${editStudent.name}`, 'success');
    setEditStudent(null);
  };

  const handleResetPassSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    showToast(`Password reset for ${resetPassStudent.name}`, 'info');
    setResetPassStudent(null);
    setNewPassword('');
  };

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Users className="w-6 h-6 text-brand-400" />
            Students Directory & User Management
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Search, filter, view profile, edit details, and reset credentials for 200 enrolled students.
          </p>
        </div>

        <button
          onClick={() => showToast('Create Student Modal ready', 'info')}
          className="bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs py-2.5 px-4 rounded-xl flex items-center gap-2 transition"
        >
          <Plus className="w-4 h-4" /> Enroll New Student
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="glass-card rounded-2xl p-4 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-500" />
          <input
            type="text"
            placeholder="Search by student name or ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter className="w-4 h-4 text-slate-500" />
          <select
            value={deptFilter}
            onChange={(e) => setDeptFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200"
          >
            <option value="All">All Departments</option>
            <option value="Computer Science">Computer Science</option>
            <option value="Electronics & Comm">Electronics & Comm</option>
            <option value="Mechanical Eng">Mechanical Eng</option>
            <option value="Civil Eng">Civil Eng</option>
          </select>
        </div>
      </div>

      {/* Students Table */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 text-slate-400 font-semibold uppercase font-mono">
              <tr>
                <th className="py-3 px-4">Student ID</th>
                <th className="py-3 px-4">Name</th>
                <th className="py-3 px-4">Department & Sem</th>
                <th className="py-3 px-4">CGPA</th>
                <th className="py-3 px-4">Focus Score</th>
                <th className="py-3 px-4">Burnout Risk</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map((st) => (
                <tr key={st.id} className="hover:bg-slate-900/40 transition">
                  <td className="py-3.5 px-4 font-mono text-brand-400 font-semibold">{st.student_id}</td>
                  <td className="py-3.5 px-4 font-semibold text-slate-100">{st.name}</td>
                  <td className="py-3.5 px-4 text-slate-400">{st.department} (Sem {st.semester})</td>
                  <td className="py-3.5 px-4 font-mono">{st.cgpa}</td>
                  <td className="py-3.5 px-4 font-bold text-emerald-400">{st.focus}</td>
                  <td className="py-3.5 px-4 font-bold text-rose-400">{st.burnout}%</td>
                  <td className="py-3.5 px-4">
                    <Badge variant={st.status === 'Active' ? 'success' : 'critical'}>{st.status}</Badge>
                  </td>
                  <td className="py-3.5 px-4 text-right space-x-1">
                    <button
                      onClick={() => setViewStudent(st)}
                      className="p-1.5 rounded-lg bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800 transition"
                      title="View Profile"
                    >
                      <Eye className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => setEditStudent(st)}
                      className="p-1.5 rounded-lg bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800 transition"
                      title="Edit Student"
                    >
                      <Edit3 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => setResetPassStudent(st)}
                      className="p-1.5 rounded-lg bg-slate-900 text-purple-400 hover:text-purple-300 border border-slate-800 transition"
                      title="Reset Password"
                    >
                      <Key className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* View Modal */}
      <Modal isOpen={!!viewStudent} onClose={() => setViewStudent(null)} title={`Student Profile: ${viewStudent?.name}`}>
        <div className="space-y-3 text-xs text-slate-300">
          <div><strong className="text-slate-200">Student ID:</strong> {viewStudent?.student_id}</div>
          <div><strong className="text-slate-200">Email:</strong> {viewStudent?.email}</div>
          <div><strong className="text-slate-200">Department:</strong> {viewStudent?.department} (Semester {viewStudent?.semester})</div>
          <div><strong className="text-slate-200">Focus Index:</strong> {viewStudent?.focus}</div>
          <div><strong className="text-slate-200">Burnout Risk:</strong> {viewStudent?.burnout}%</div>
        </div>
      </Modal>

      {/* Edit Modal */}
      {editStudent && (
        <Modal isOpen={!!editStudent} onClose={() => setEditStudent(null)} title={`Edit Student: ${editStudent.name}`}>
          <form onSubmit={handleEditSubmit} className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-300 mb-1">Full Name</label>
              <input
                type="text"
                value={editStudent.name}
                onChange={(e) => setEditStudent({ ...editStudent, name: e.target.value })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-slate-200"
              />
            </div>
            <div>
              <label className="block text-slate-300 mb-1">Department</label>
              <input
                type="text"
                value={editStudent.department}
                onChange={(e) => setEditStudent({ ...editStudent, department: e.target.value })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-slate-200"
              />
            </div>
            <button type="submit" className="w-full bg-brand-600 text-white font-semibold py-2 rounded-xl">
              Save Changes
            </button>
          </form>
        </Modal>
      )}

      {/* Reset Password Modal */}
      {resetPassStudent && (
        <Modal isOpen={!!resetPassStudent} onClose={() => setResetPassStudent(null)} title={`Reset Password: ${resetPassStudent.name}`}>
          <form onSubmit={handleResetPassSubmit} className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-300 mb-1">New Password</label>
              <input
                type="password"
                placeholder="Enter new password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-slate-200"
              />
            </div>
            <button type="submit" className="w-full bg-purple-600 text-white font-semibold py-2 rounded-xl">
              Reset Password
            </button>
          </form>
        </Modal>
      )}
    </div>
  );
};
