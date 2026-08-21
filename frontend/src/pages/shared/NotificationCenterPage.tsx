import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Bell, AlertTriangle, CheckCircle2, Info, Filter, ShieldAlert } from 'lucide-react';
import { Badge } from '../../components/Badge';
import { API_BASE_URL } from '../../services/api';

interface NotificationItem {
  id: string | number;
  title: string;
  text?: string;
  message?: string;
  time?: string;
  created_at?: string;
  type: string;
  severity?: string;
  is_read?: boolean;
}

export const NotificationCenterPage: React.FC = () => {
  const { user } = useAuth();
  const isParent = user?.role === 'parent';

  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const studentId = (user as any)?.id || 1;
    fetch(`${API_BASE_URL}/notifications/${studentId}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(localStorage.getItem('studiq_token') ? { Authorization: `Bearer ${localStorage.getItem('studiq_token')}` } : {})
      }
    })
      .then(r => r.json())
      .then((data: any[]) => {
        const mapped: NotificationItem[] = data.map(n => ({
          id: n.id,
          title: n.title,
          text: n.message,
          type: n.severity === 'high' ? 'warning' : n.type === 'parent_alert' ? 'critical' : n.type === 'parent_approval' && n.is_read ? 'success' : 'info',
          time: n.created_at ? new Date(n.created_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : '—',
        }));
        setNotifications(mapped.length > 0 ? mapped : getFallback());
        setLoading(false);
      })
      .catch(() => {
        setNotifications(getFallback());
        setLoading(false);
      });
  }, [user]);

  const getFallback = (): NotificationItem[] => {
    if (isParent) {
      return [
        { id: 101, title: 'Entertainment Limit Exceeded', text: 'Alex Mercer exceeded the daily entertainment limit (95 mins spent).', time: '15 mins ago', type: 'warning' },
        { id: 102, title: '5 Break Warnings Ignored', text: 'Alex Mercer ignored 5 continuous study break popups today.', time: '2 hours ago', type: 'critical' },
        { id: 103, title: 'Focus Score Decreased', text: 'Weekly Focus Score decreased from 88 to 82 index.', time: 'Yesterday', type: 'warning' },
        { id: 104, title: 'Burnout Risk Increased', text: 'Burnout Risk model updated to Medium Fatigue level.', time: '2 days ago', type: 'warning' },
        { id: 105, title: 'Weekly Intelligence Report Available', text: "Alex Mercer's Weekly Report (July 25 - July 31) is available for PDF download.", time: '3 days ago', type: 'info' },
      ];
    }
    return [
      { id: 1, title: 'Entertainment Limit Exceeded', text: "You exceeded today's 90-minute weekday entertainment limit.", time: '10 mins ago', type: 'warning' },
      { id: 2, title: 'Goal Completed', text: 'Completed daily goal: Dynamic Programming Assignment Set #3.', time: '1 hour ago', type: 'success' },
      { id: 3, title: 'Assignment Due Reminder', text: 'CS302 ML Pipeline Assignment due in 24 hours.', time: '3 hours ago', type: 'info' },
      { id: 4, title: 'Quiz Reminder', text: 'Midterm Quiz 2 scheduled for tomorrow at 10:00 AM.', time: '5 hours ago', type: 'info' },
      { id: 5, title: 'Pomodoro Break Reminder', text: 'Completed 50-minute study block. Take a 10-minute movement break.', time: 'Yesterday', type: 'info' },
    ];
  };

  return (
    <div className="space-y-6 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Bell className="w-6 h-6 text-brand-400" />
            {isParent ? 'Parent Alerts & Notification Center' : 'Notification Center'}
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            {isParent
              ? 'Real-time alert stream for student entertainment limits, warning escalations, and report availability.'
              : 'Alerts for goals, assignment reminders, quiz schedules, and study mode notifications.'}
          </p>
        </div>
      </div>

      <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-3">
        {loading ? (
          <div className="py-8 text-center text-slate-400 text-sm">
            <div className="w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            Loading notifications...
          </div>
        ) : notifications.length === 0 ? (
          <div className="py-8 text-center text-slate-500 text-sm">No notifications yet.</div>
        ) : (
          notifications.map((n) => (
            <div
              key={n.id}
              className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start justify-between gap-4 hover:bg-slate-900/80 transition"
            >
              <div className="flex items-start gap-3">
                <div className="mt-0.5">
                  {n.type === 'warning' || n.type === 'critical' ? (
                    <AlertTriangle className={`w-5 h-5 ${n.type === 'critical' ? 'text-rose-400' : 'text-amber-400'}`} />
                  ) : n.type === 'success' ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  ) : (
                    <Info className="w-5 h-5 text-brand-400" />
                  )}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-bold text-slate-100">{n.title}</h3>
                    <Badge variant={n.type === 'critical' ? 'critical' : n.type === 'warning' ? 'medium' : 'info'}>
                      {n.type.toUpperCase()}
                    </Badge>
                  </div>
                  <p className="text-xs text-slate-300 mt-1">{n.text || n.message}</p>
                </div>
              </div>
              <span className="text-[11px] font-mono text-slate-500 whitespace-nowrap">{n.time}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
