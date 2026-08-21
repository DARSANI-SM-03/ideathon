import React, { useEffect, useState } from 'react';
import { MentorService } from '../../services/mentorService';
import { MentorStudent, PriorityStudent, Meeting } from '../../types';
import { Modal } from '../../components/Modal';
import { useNavigate } from 'react-router-dom';
import {
  Award,
  ShieldAlert,
  Users,
  Calendar,
  AlertTriangle,
  Radio,
  Bell,
  CheckCircle2,
  Send,
  Building,
  UserX,
  MessageSquare
} from 'lucide-react';

import { ApiService } from '../../services/api';

export const MentorDashboard: React.FC = () => {
  const [students, setStudents] = useState<MentorStudent[]>([]);
  const [priorityQueue, setPriorityQueue] = useState<PriorityStudent[]>([]);
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionModal, setActionModal] = useState<{ open: boolean; title: string; studentName: string; type: 'session' | 'notify' | 'telemetry' }>({
    open: false,
    title: '',
    studentName: '',
    type: 'session'
  });
  const [modalSuccess, setModalSuccess] = useState(false);
  const navigate = useNavigate();

  const loadMentorData = () => {
    Promise.all([
      MentorService.getAssignedStudents(),
      MentorService.getPriorityQueue(),
      MentorService.getMeetings(),
    ]).then(([stuData, prioData, meetData]) => {
      setStudents(stuData);
      setPriorityQueue(prioData);
      setMeetings(meetData);
      setLoading(false);
    });
  };

  useEffect(() => {
    loadMentorData();
    const interval = setInterval(() => {
      loadMentorData();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="p-12 text-center text-slate-400 font-sans">
        <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        Loading Faculty Mentor Action Hub...
      </div>
    );
  }

  const highRiskStudents = students.filter(s => s.burnoutRisk === 'high' || s.burnoutRisk === 'critical');
  const lowFocusStudents = students.filter(s => s.focusScore < 70);

  const triggerAction = (studentName: string, type: 'session' | 'notify') => {
    const title = type === 'session'
      ? `Schedule Intervention Session with ${studentName}`
      : `Send Automated Parent Warning for ${studentName}`;

    setActionModal({ open: true, title, studentName, type });
  };

  const handleModalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (actionModal.type === 'session') {
      await ApiService.scheduleIntervention(actionModal.studentName, 'Intervention scheduled via Faculty Dashboard');
    } else if (actionModal.type === 'notify') {
      await ApiService.sendWarning(actionModal.studentName, 'Automated parent warning sent via Faculty Dashboard');
    }

    setModalSuccess(true);
    setTimeout(() => {
      setModalSuccess(false);
      setActionModal({ ...actionModal, open: false });
      loadMentorData();
    }, 1200);
  };

  return (
    <div className="space-y-6 pb-12 font-sans">
      {/* Header */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-white">Faculty Mentor Action Dashboard</h1>
            <span className="px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 text-xs font-mono font-bold">
              High Risk Intervention Priority
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Predictive burnout queue, active alerts, counseling queue, and immediate intervention triggers.
          </p>
        </div>

        <button
          onClick={() => navigate('/mentor/students')}
          className="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold flex items-center gap-2 transition"
        >
          <Users className="w-4 h-4" /> View Full Mentee Roster ({students.length})
        </button>
      </div>

      {/* ACTION KPI STATS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card rounded-2xl p-5 border border-slate-800">
          <span className="text-xs font-semibold text-slate-400 uppercase font-mono block">High Risk Students</span>
          <span className="text-3xl font-black text-rose-400 mt-1 block">{highRiskStudents.length}</span>
          <span className="text-[11px] text-rose-400/80 font-medium">Requires Urgent Intervention</span>
        </div>

        <div className="glass-card rounded-2xl p-5 border border-slate-800">
          <span className="text-xs font-semibold text-slate-400 uppercase font-mono block">Today's Active Alerts</span>
          <span className="text-3xl font-black text-amber-400 mt-1 block">{priorityQueue.length} Alerts</span>
          <span className="text-[11px] text-amber-400/80 font-medium">Late Night & Fatigue Spikes</span>
        </div>

        <div className="glass-card rounded-2xl p-5 border border-slate-800">
          <span className="text-xs font-semibold text-slate-400 uppercase font-mono block">Counseling Queue</span>
          <span className="text-3xl font-black text-brand-400 mt-1 block">{meetings.length} Pending</span>
          <span className="text-[11px] text-slate-400">Scheduled Parent & Student Meetings</span>
        </div>

        <div className="glass-card rounded-2xl p-5 border border-slate-800">
          <span className="text-xs font-semibold text-slate-400 uppercase font-mono block">Dept Attendance Rate</span>
          <span className="text-3xl font-black text-emerald-400 mt-1 block">
            {students.length > 0 ? (students.reduce((acc, s) => acc + s.attendance, 0) / students.length).toFixed(1) : '90.0'}%
          </span>
          <span className="text-[11px] text-emerald-400 font-medium">Compliant with Standards</span>
        </div>
      </div>


      {/* HIGH RISK STUDENTS QUEUE (HERO ACTION SECTION) */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-rose-400" />
            <h3 className="text-base font-bold text-white">High Risk Students — Immediate Action Required</h3>
          </div>
          <span className="text-xs font-mono text-rose-400 bg-rose-500/10 px-2.5 py-0.5 rounded-full border border-rose-500/20">
            {highRiskStudents.length} Students At Risk
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {priorityQueue.map((item) => (
            <div key={item.student.id} className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 flex flex-col justify-between space-y-3">
              <div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 flex items-center justify-center font-bold text-xs">
                      {item.student.name.charAt(0)}
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-white">{item.student.name}</h4>
                      <span className="text-[10px] text-slate-400 font-mono">{item.student.studentId} • {item.student.department}</span>
                    </div>
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 text-xs font-bold font-mono">
                    Risk: {item.priorityScore}/100
                  </span>
                </div>
                <p className="text-xs text-slate-300 bg-slate-950 p-2.5 rounded-lg border border-slate-800/80 mt-3 leading-relaxed">
                  {item.reason}
                </p>
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800">
                <button
                  onClick={() => triggerAction(item.student.name, 'session')}
                  className="p-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-[11px] font-bold flex items-center justify-center gap-1.5 transition shadow"
                >
                  <Calendar className="w-3.5 h-3.5" /> Schedule Counseling
                </button>

                <button
                  onClick={() => triggerAction(item.student.name, 'notify')}
                  className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-amber-400 text-[11px] font-bold flex items-center justify-center gap-1.5 transition border border-slate-700"
                >
                  <Bell className="w-3.5 h-3.5" /> Parent Alert
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* TODAY'S ALERTS & COUNSELING QUEUE */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Today's Alerts & Meeting Requests */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Calendar className="w-5 h-5 text-indigo-400" /> Pending Meeting Requests
            </h3>
            <span className="text-xs font-mono text-slate-400">{meetings.length} Scheduled</span>
          </div>

          <div className="space-y-3">
            {meetings.map((m) => (
              <div key={m.id} className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white">{m.student?.name || (m as any).studentName || 'Student'}</span>
                    <span className="text-[10px] text-brand-400 bg-brand-500/10 px-2 py-0.5 rounded font-mono">{m.type}</span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">{m.notes}</p>
                </div>
                <div className="text-right shrink-0 font-mono text-xs text-slate-300">
                  <div>{m.date}</div>
                  <div className="text-[10px] text-slate-500">{m.time}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Low Focus Students Filterable List */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <UserX className="w-5 h-5 text-amber-400" /> Low Focus Mentees (&lt; 70%)
            </h3>
            <span className="text-xs font-mono text-amber-400">{lowFocusStudents.length} Students</span>
          </div>

          <div className="space-y-2">
            {lowFocusStudents.map((s) => (
              <div key={s.id} className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
                <div>
                  <span className="font-bold text-white block">{s.name}</span>
                  <span className="text-[11px] text-slate-400">{s.department}</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-right font-mono">
                    <span className="text-amber-400 font-bold">{s.focusScore}% Focus</span>
                    <span className="block text-[10px] text-slate-500">{(s.totalStudyHours || (s as any).studyHours || 0)}h study</span>
                  </div>

                  <button
                    onClick={() => triggerAction(s.name, 'session')}
                    className="p-1.5 rounded-lg bg-brand-600/20 text-brand-400 hover:bg-brand-600 hover:text-white transition"
                    title="Schedule Quick Intervention"
                  >
                    <Send className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Action Trigger Modal */}
      <Modal
        isOpen={actionModal.open}
        onClose={() => setActionModal({ ...actionModal, open: false })}
        title={actionModal.title}
      >
        {modalSuccess ? (
          <div className="py-6 text-center space-y-2">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
            <h4 className="text-base font-bold text-white">Action Dispatched Successfully!</h4>
            <p className="text-xs text-slate-400">Recorded in faculty log & notified to relevant parties.</p>
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
                placeholder="e.g., Reviewing late night screen spikes and recommending 15-minute Pomodoro breaks."
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-brand-600 hover:bg-brand-500 text-white font-bold py-2.5 rounded-xl text-xs shadow-lg transition"
            >
              Dispatch Action & Record in Logs
            </button>
          </form>
        )}
      </Modal>
    </div>
  );
};
