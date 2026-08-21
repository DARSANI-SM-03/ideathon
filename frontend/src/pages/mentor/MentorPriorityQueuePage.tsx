import React, { useEffect, useState } from 'react';
import { ShieldAlert, AlertTriangle, Calendar, CheckCircle2, Bell } from 'lucide-react';
import { MentorService } from '../../services/mentorService';
import { PriorityStudent } from '../../types';
import { Modal } from '../../components/Modal';
import { ApiService } from '../../services/api';
import { useToast } from '../../context/ToastContext';

export const MentorPriorityQueuePage: React.FC = () => {
  const [queue, setQueue] = useState<PriorityStudent[]>([]);
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  const [actionModal, setActionModal] = useState<{
    open: boolean;
    title: string;
    studentName: string;
    type: 'session' | 'notify';
  }>({ open: false, title: '', studentName: '', type: 'session' });
  const [modalNotes, setModalNotes] = useState('');
  const [modalSuccess, setModalSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    MentorService.getPriorityQueue().then(res => {
      setQueue(res);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const triggerAction = (studentName: string, type: 'session' | 'notify') => {
    const title = type === 'session'
      ? `Schedule Intervention Session — ${studentName}`
      : `Send Parent Alert — ${studentName}`;
    setModalNotes('');
    setModalSuccess(false);
    setActionModal({ open: true, title, studentName, type });
  };

  const handleModalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (actionModal.type === 'session') {
        await ApiService.scheduleIntervention(actionModal.studentName, modalNotes);
        showToast(`Intervention scheduled for ${actionModal.studentName}`, 'success');
      } else {
        await ApiService.sendWarning(actionModal.studentName, modalNotes);
        showToast(`Parent alert sent for ${actionModal.studentName}`, 'success');
      }
      setModalSuccess(true);
      setTimeout(() => {
        setModalSuccess(false);
        setActionModal(prev => ({ ...prev, open: false }));
      }, 1200);
    } catch {
      showToast('Action failed. Please try again.', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Mentee Priority Intervention Queue</h1>
        <p className="text-xs text-slate-400 mt-1">Autonomous risk prioritization engine flagging high burnout &amp; academic risk</p>
      </div>

      <div className="space-y-4">
        {queue.length === 0 && (
          <div className="glass-card p-8 rounded-2xl border border-slate-800 text-center text-slate-400 text-sm">
            No students currently flagged for priority intervention.
          </div>
        )}
        {queue.map((item) => (
          <div key={item.student.id} className="glass-card p-6 rounded-2xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-rose-500 to-orange-600 flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-rose-500/20">
                  {item.student.name.charAt(0)}
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">{item.student.name}</h3>
                  <p className="text-xs text-slate-400 font-mono">{item.student.studentId} &bull; Semester {item.student.semester} &bull; {item.student.department}</p>
                </div>
              </div>
              <span className="px-3 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 text-xs font-bold font-mono">
                Priority Index: {item.priorityScore}
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 text-xs text-slate-200">
              <p className="font-semibold text-rose-400 mb-1">Reason for Intervention:</p>
              <p>{item.reason}</p>
            </div>

            <div className="flex items-center justify-between pt-2">
              <div className="flex gap-2">
                {item.categories.map((cat) => (
                  <span key={cat} className="px-2 py-0.5 rounded text-[10px] uppercase font-mono bg-slate-800 text-slate-300">
                    {cat.replace('_', ' ')}
                  </span>
                ))}
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => triggerAction(item.student.name, 'session')}
                  className="px-3 py-1.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold flex items-center gap-1.5 transition"
                >
                  <Calendar className="w-3.5 h-3.5" /> Schedule Counseling
                </button>
                <button
                  onClick={() => triggerAction(item.student.name, 'notify')}
                  className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-amber-400 text-xs font-semibold flex items-center gap-1.5 border border-slate-700 transition"
                >
                  <Bell className="w-3.5 h-3.5" /> Parent Alert
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Action Modal */}
      <Modal
        isOpen={actionModal.open}
        onClose={() => setActionModal(prev => ({ ...prev, open: false }))}
        title={actionModal.title}
      >
        {modalSuccess ? (
          <div className="py-6 text-center space-y-2">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
            <h4 className="text-base font-bold text-white">Action Dispatched Successfully!</h4>
            <p className="text-xs text-slate-400">Recorded in faculty log &amp; notified to relevant parties.</p>
          </div>
        ) : (
          <form onSubmit={handleModalSubmit} className="space-y-4">
            <p className="text-xs text-slate-300">
              Confirming action for mentee <strong className="text-brand-400">{actionModal.studentName}</strong>.
            </p>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Intervention Notes / Agenda</label>
              <textarea
                required
                rows={3}
                value={modalNotes}
                onChange={e => setModalNotes(e.target.value)}
                placeholder="e.g., Reviewing late night screen spikes and recommending 15-minute Pomodoro breaks."
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-brand-600 hover:bg-brand-500 disabled:opacity-60 text-white font-bold py-2.5 rounded-xl text-xs shadow-lg transition"
            >
              {submitting ? 'Dispatching...' : 'Dispatch Action & Record in Logs'}
            </button>
          </form>
        )}
      </Modal>
    </div>
  );
};
