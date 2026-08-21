import React, { useEffect, useState } from 'react';
import { Award, Calendar, Plus, CheckCircle2 } from 'lucide-react';
import { MentorService } from '../../services/mentorService';
import { CounselingCase } from '../../types';
import { Modal } from '../../components/Modal';
import { ApiService } from '../../services/api';
import { useToast } from '../../context/ToastContext';

export const MentorCounselingPage: React.FC = () => {
  const [cases, setCases] = useState<CounselingCase[]>([]);
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalSuccess, setModalSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [studentName, setStudentName] = useState('');
  const [caseReason, setCaseReason] = useState('');
  const [caseNotes, setCaseNotes] = useState('');

  useEffect(() => {
    MentorService.getCounselingCases().then(res => {
      setCases(res);
      setLoading(false);
    });
  }, []);

  const handleOpenModal = () => {
    setStudentName('');
    setCaseReason('');
    setCaseNotes('');
    setModalSuccess(false);
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await ApiService.scheduleIntervention(studentName, caseReason + (caseNotes ? ` — ${caseNotes}` : ''));
      showToast(`Counseling case opened for ${studentName}`, 'success');
      setModalSuccess(true);
      // Add optimistic UI entry
      const newCase: CounselingCase = {
        id: `c_new_${Date.now()}`,
        studentId: '0',
        student: { id: '0', name: studentName, department: '—', semester: 0 },
        mentorId: '50',
        priority: 'urgent',
        reason: caseReason,
        notes: caseNotes,
        status: 'scheduled',
        scheduledDate: new Date().toISOString(),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      setCases(prev => [newCase, ...prev]);
      setTimeout(() => {
        setModalSuccess(false);
        setIsModalOpen(false);
      }, 1200);
    } catch {
      showToast('Failed to create counseling case. Try again.', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Academic Counseling Sessions</h1>
          <p className="text-xs text-slate-400 mt-1">Manage 1-on-1 counseling cases, intervention notes, and progress logs</p>
        </div>
        <button
          onClick={handleOpenModal}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold transition"
        >
          <Plus className="w-4 h-4" /> New Counseling Case
        </button>
      </div>

      <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
        {!loading && cases.length === 0 && (
          <div className="text-center text-slate-400 text-sm py-8">
            No active counseling cases. Click "New Counseling Case" to create one.
          </div>
        )}
        {cases.map((c) => (
          <div key={c.id} className="p-4 rounded-xl glass-panel border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-brand-500/20 text-brand-400 flex items-center justify-center font-bold text-xs">
                  {c.student.name.charAt(0)}
                </div>
                <div>
                  <h3 className="text-xs font-bold text-white">{c.student.name}</h3>
                  <span className="text-[10px] text-slate-400">{c.student.department} &bull; Semester {c.student.semester}</span>
                </div>
              </div>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 uppercase font-mono">
                {c.status}
              </span>
            </div>

            <p className="text-xs text-slate-200">{c.reason}</p>
            {c.notes && <p className="text-xs text-slate-400 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">{c.notes}</p>}
          </div>
        ))}
      </div>

      {/* New Counseling Case Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="New Academic Counseling Case"
      >
        {modalSuccess ? (
          <div className="py-6 text-center space-y-2">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
            <h4 className="text-base font-bold text-white">Case Created Successfully!</h4>
            <p className="text-xs text-slate-400">Counseling session recorded in faculty logs.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Student Full Name</label>
              <input
                type="text"
                required
                value={studentName}
                onChange={e => setStudentName(e.target.value)}
                placeholder="e.g. Sophia Patel"
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Reason / Issue</label>
              <input
                type="text"
                required
                value={caseReason}
                onChange={e => setCaseReason(e.target.value)}
                placeholder="e.g. High burnout risk with declining attendance"
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Session Notes (optional)</label>
              <textarea
                rows={3}
                value={caseNotes}
                onChange={e => setCaseNotes(e.target.value)}
                placeholder="e.g. Reviewing screen usage patterns and advising structured study schedule."
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-brand-600 hover:bg-brand-500 disabled:opacity-60 text-white font-bold py-2.5 rounded-xl text-xs shadow-lg transition"
            >
              {submitting ? 'Creating Case...' : 'Create Counseling Case'}
            </button>
          </form>
        )}
      </Modal>
    </div>
  );
};
