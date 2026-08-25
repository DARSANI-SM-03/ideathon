import React, { useState, useEffect } from 'react';
import { Target, Plus, CheckCircle2, Clock, BookOpen, Award, Activity } from 'lucide-react';
import { useToast } from '../../context/ToastContext';
import { Modal } from '../../components/Modal';
import { useAuth } from '../../context/AuthContext';
import { API_BASE_URL } from '../../services/api';

interface GoalItem {
  id: number;
  category: string;
  title: string;
  current: number;
  target: number;
  unit: string;
  progress: number;
  done: boolean;
}

const DEFAULT_GOALS: GoalItem[] = [
  { id: 1, category: 'Study Hours', title: 'Daily Productive Coding', current: 5, target: 6, unit: 'hrs', progress: 83, done: false },
  { id: 2, category: 'Assignments', title: 'CS302 ML Assignment #3', current: 1, target: 1, unit: 'task', progress: 100, done: true },
  { id: 3, category: 'Revision', title: 'Database Indexing Notes', current: 2, target: 3, unit: 'topics', progress: 66, done: false },
  { id: 4, category: 'Practice Questions', title: 'LeetCode Algorithm Problems', current: 15, target: 20, unit: 'solved', progress: 75, done: false },
  { id: 5, category: 'Exercise', title: 'Evening Walk / Screen Break', current: 30, target: 30, unit: 'mins', progress: 100, done: true }
];

export const StudyGoalsPage: React.FC = () => {
  const { user } = useAuth();
  const storageKey = `studiq_goals_${user?.id || 'default'}`;
  const { showToast } = useToast();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newCategory, setNewCategory] = useState('Study Hours');
  const [newTarget, setNewTarget] = useState(5);
  const [newUnit, setNewUnit] = useState('hrs');

  const [goals, setGoals] = useState<GoalItem[]>(() => {
    try {
      const saved = localStorage.getItem(storageKey);
      if (saved) return JSON.parse(saved);
    } catch {}
    return DEFAULT_GOALS;
  });

  // Persist goals to localStorage on every change
  useEffect(() => {
    try {
      localStorage.setItem(storageKey, JSON.stringify(goals));
    } catch {}
  }, [goals, storageKey]);

  const toggleDone = (id: number) => {
    setGoals((prev) =>
      prev.map((g) => {
        if (g.id === id) {
          const nextState = !g.done;
          showToast(nextState ? `Goal '${g.title}' Completed! ✅` : `Goal '${g.title}' Marked as Pending`, 'info');
          // Attempt to sync with backend
          fetch(`${API_BASE_URL}/students/${user?.user_identifier || 'STU-2026-001'}/goals/${id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ done: nextState })
          }).catch(() => {}); // Silently fail if endpoint not yet implemented
          return { ...g, done: nextState };
        }
        return g;
      })
    );
  };

  const handleAddGoal = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    const newGoal = {
      id: Date.now(),
      category: newCategory,
      title: newTitle,
      current: 0,
      target: newTarget,
      unit: newUnit,
      progress: 0,
      done: false
    };

    setGoals([newGoal, ...goals]);
    showToast(`New goal '${newTitle}' created successfully!`, 'success');
    // Attempt to sync with backend
    fetch(`${API_BASE_URL}/students/${user?.user_identifier || 'STU-2026-001'}/goals`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newGoal)
    }).catch(() => {}); // Silently fail if endpoint not yet implemented
    setIsModalOpen(false);
    setNewTitle('');
  };

  return (
    <div className="space-y-6 pb-12 font-sans">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Target className="w-6 h-6 text-brand-400" />
            Study Goals & Goal Completion Tracker
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Track daily and weekly study milestones: Study Hours, Assignments, Revision, Practice Questions, and Exercise.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs py-2.5 px-4 rounded-xl flex items-center gap-2 transition shadow-lg shadow-brand-500/20"
        >
          <Plus className="w-4 h-4" /> Add Custom Goal
        </button>
      </div>

      {/* Goal Categories Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {goals.map((g) => (
          <div key={g.id} className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold uppercase tracking-wider text-brand-400 font-mono">
                  {g.category}
                </span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                  g.done ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                }`}>
                  {g.done ? 'Completed' : 'In Progress'}
                </span>
              </div>

              <h3 className="text-base font-bold text-slate-100 mb-1">{g.title}</h3>
              <p className="text-xs text-slate-400 font-mono mb-4">
                Target: {g.current} / {g.target} {g.unit} ({g.progress}%)
              </p>

              {/* Progress Bar */}
              <div className="w-full h-3 rounded-full bg-slate-900 border border-slate-800 overflow-hidden mb-4">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${
                    g.done ? 'bg-emerald-500' : 'bg-gradient-to-r from-brand-600 to-emerald-500'
                  }`}
                  style={{ width: `${g.progress}%` }}
                />
              </div>
            </div>

            <button
              onClick={() => toggleDone(g.id)}
              className={`w-full py-2 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition ${
                g.done
                  ? 'bg-slate-900 text-slate-400 border border-slate-800'
                  : 'bg-brand-600/20 hover:bg-brand-600/30 text-brand-300 border border-brand-500/30'
              }`}
            >
              <CheckCircle2 className="w-4 h-4" />
              {g.done ? 'Mark as Pending' : 'Mark as Completed'}
            </button>
          </div>
        ))}
      </div>

      {/* Add Custom Goal Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Add New Study Goal"
      >
        <form onSubmit={handleAddGoal} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Goal Title</label>
            <input
              type="text"
              required
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="e.g. Complete 5 Operating Systems Practice Questions"
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
            />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Category</label>
              <select
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none"
              >
                <option value="Study Hours">Study Hours</option>
                <option value="Assignments">Assignments</option>
                <option value="Revision">Revision</option>
                <option value="Practice Questions">Practice Questions</option>
                <option value="Exercise">Exercise</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Target Number</label>
              <input
                type="number"
                min="1"
                value={newTarget}
                onChange={(e) => setNewTarget(Number(e.target.value))}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Unit</label>
              <input
                type="text"
                value={newUnit}
                onChange={(e) => setNewUnit(e.target.value)}
                placeholder="hrs, tasks, topics"
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full bg-brand-600 hover:bg-brand-500 text-white font-bold py-2.5 rounded-xl text-xs shadow-lg transition"
          >
            Create Goal
          </button>
        </form>
      </Modal>
    </div>
  );
};
