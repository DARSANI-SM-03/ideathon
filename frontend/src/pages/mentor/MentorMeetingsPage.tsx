import React, { useEffect, useState } from 'react';
import { Calendar, Clock, Video, Plus, CheckCircle2 } from 'lucide-react';
import { MentorService } from '../../services/mentorService';
import { Meeting } from '../../types';
import { Modal } from '../../components/Modal';
import { ApiService } from '../../services/api';
import { useToast } from '../../context/ToastContext';

export const MentorMeetingsPage: React.FC = () => {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const { showToast } = useToast();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalSuccess, setModalSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [meetingStudent, setMeetingStudent] = useState('');
  const [meetingDate, setMeetingDate] = useState('');
  const [meetingTime, setMeetingTime] = useState('');
  const [meetingType, setMeetingType] = useState('Student');
  const [meetingNotes, setMeetingNotes] = useState('');

  useEffect(() => {
    MentorService.getMeetings().then(setMeetings);
  }, []);

  const handleOpenModal = () => {
    setMeetingStudent('');
    setMeetingDate('');
    setMeetingTime('');
    setMeetingType('Student');
    setMeetingNotes('');
    setModalSuccess(false);
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await ApiService.scheduleIntervention(
        meetingStudent,
        `${meetingType} Meeting scheduled for ${meetingDate} at ${meetingTime}. Notes: ${meetingNotes}`
      );
      showToast(`Meeting scheduled with ${meetingStudent}`, 'success');
      setModalSuccess(true);
      // Optimistic UI update
      const newMeeting: Meeting = {
        id: `m_new_${Date.now()}`,
        type: meetingType as any,
        purpose: meetingNotes || `${meetingType} Advisory Session`,
        student: { id: '0', name: meetingStudent, department: '—', semester: 0 } as any,
        date: meetingDate,
        time: meetingTime,
        location: 'TBD',
        notes: meetingNotes,
        status: 'scheduled' as any,
        isOnline: false,
        meetingLink: '',
        createdAt: new Date().toISOString(),
      };
      setMeetings(prev => [newMeeting, ...prev]);
      setTimeout(() => {
        setModalSuccess(false);
        setIsModalOpen(false);
      }, 1200);
    } catch {
      showToast('Failed to schedule meeting. Try again.', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Mentorship Meetings</h1>
          <p className="text-xs text-slate-400 mt-1">Schedule and review student, parent, and joint advisory meetings</p>
        </div>
        <button
          onClick={handleOpenModal}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold transition"
        >
          <Plus className="w-4 h-4" /> Schedule Meeting
        </button>
      </div>

      <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
        {meetings.length === 0 && (
          <div className="text-center text-slate-400 text-sm py-8">
            No meetings scheduled. Click "Schedule Meeting" to create one.
          </div>
        )}
        {meetings.map((m) => (
          <div key={m.id} className="p-4 rounded-xl glass-panel border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-start gap-4">
              <div className="p-3 rounded-2xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                <Calendar className="w-6 h-6" />
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-bold">
                  {m.type} Meeting
                </span>
                <h3 className="text-sm font-bold text-white mt-1">{m.purpose}</h3>
                <p className="text-xs text-slate-400">With: <strong className="text-slate-200">{m.student.name}</strong> &bull; {m.date} at {m.time}</p>
                <p className="text-xs text-brand-400 font-mono mt-1">{m.location}</p>
              </div>
            </div>

            {m.isOnline && m.meetingLink && (
              <a href={m.meetingLink} target="_blank" rel="noreferrer" className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-brand-400 text-xs font-semibold">
                <Video className="w-4 h-4" /> Join Virtual Meeting
              </a>
            )}
          </div>
        ))}
      </div>

      {/* Schedule Meeting Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Schedule New Meeting"
      >
        {modalSuccess ? (
          <div className="py-6 text-center space-y-2">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
            <h4 className="text-base font-bold text-white">Meeting Scheduled!</h4>
            <p className="text-xs text-slate-400">Session recorded in faculty logs.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Student / Attendee Name</label>
              <input
                type="text"
                required
                value={meetingStudent}
                onChange={e => setMeetingStudent(e.target.value)}
                placeholder="e.g. Marcus Chen"
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Meeting Type</label>
                <select
                  value={meetingType}
                  onChange={e => setMeetingType(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none"
                >
                  <option value="Student">Student</option>
                  <option value="Parent">Parent</option>
                  <option value="Joint">Joint</option>
                  <option value="Advisory">Advisory</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Date</label>
                <input
                  type="date"
                  required
                  value={meetingDate}
                  onChange={e => setMeetingDate(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Time</label>
              <input
                type="time"
                required
                value={meetingTime}
                onChange={e => setMeetingTime(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Agenda / Notes</label>
              <textarea
                rows={3}
                value={meetingNotes}
                onChange={e => setMeetingNotes(e.target.value)}
                placeholder="e.g. Discuss Q3 progress, burnout risk, and action plan."
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-brand-600 hover:bg-brand-500 disabled:opacity-60 text-white font-bold py-2.5 rounded-xl text-xs shadow-lg transition"
            >
              {submitting ? 'Scheduling...' : 'Confirm & Schedule Meeting'}
            </button>
          </form>
        )}
      </Modal>
    </div>
  );
};
