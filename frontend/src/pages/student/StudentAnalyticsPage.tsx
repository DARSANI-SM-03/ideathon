import React from 'react';
import {
  LineChart, Line, BarChart, Bar, AreaChart, Area, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend
} from 'recharts';
import { BarChart3, TrendingUp, Calendar, Clock, Tv } from 'lucide-react';

import { ApiService } from '../../services/api';

export const StudentAnalyticsPage: React.FC = () => {
  const [weeklyData, setWeeklyData] = React.useState<any[]>([]);
  const [monthlyData, setMonthlyData] = React.useState<any[]>([
    { week: 'Week 1', focus: 82, assignments: 88 },
    { week: 'Week 2', focus: 85, assignments: 92 },
    { week: 'Week 3', focus: 87, assignments: 95 },
    { week: 'Week 4', focus: 89, assignments: 94 },
  ]);
  const [loading, setLoading] = React.useState<boolean>(true);

  React.useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const dashboard = await ApiService.get('/students/1/dashboard');
        if (dashboard && dashboard.weekly_analytics && dashboard.weekly_analytics.length > 0) {
          const formatted = dashboard.weekly_analytics.map((item: any) => ({
            day: item.day,
            focus: item.focus || 85,
            burnout: item.burnout || 15,
            attendance: 95,
            productive: item.study_hours || 4.0,
            entertainment: roundNumber((item.entertainment_mins || 30) / 60, 1)
          }));
          setWeeklyData(formatted);
        } else {
          setWeeklyData([
            { day: 'Mon', focus: 85, burnout: 15, attendance: 95, productive: 4.5, entertainment: 0.8 },
            { day: 'Tue', focus: 88, burnout: 14, attendance: 95, productive: 5.0, entertainment: 0.5 },
            { day: 'Wed', focus: 90, burnout: 12, attendance: 95, productive: 5.5, entertainment: 0.4 },
            { day: 'Thu', focus: 84, burnout: 16, attendance: 95, productive: 4.0, entertainment: 1.0 },
            { day: 'Fri', focus: 86, burnout: 15, attendance: 95, productive: 4.8, entertainment: 0.6 },
            { day: 'Sat', focus: 89, burnout: 13, attendance: 95, productive: 5.2, entertainment: 0.7 },
            { day: 'Sun', focus: 87, burnout: 14, attendance: 95, productive: 4.6, entertainment: 0.5 },
          ]);
        }
      } catch {
        // Fallback
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  const roundNumber = (val: number, decimals: number) => {
    const factor = Math.pow(10, decimals);
    return Math.round(val * factor) / factor;
  };

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-brand-400" />
          Academic Analytics & Behavior Intelligence
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Historical trends for Focus, Burnout, Attendance, Assignment completion, Entertainment usage, and Weekly/Monthly comparisons.
        </p>
      </div>

      {/* Grid 1: Focus Score Trend & Burnout Trend */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Focus Score Trend */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-emerald-400" />
            Focus Score Trend (Weekly)
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" stroke="#64748b" tick={{ fontSize: 12 }} />
                <YAxis domain={[50, 100]} stroke="#64748b" tick={{ fontSize: 12 }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }} />
                <Area type="monotone" dataKey="focus" name="Focus Score" stroke="#10b981" fill="#10b981" fillOpacity={0.2} strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Burnout Risk Trend */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-rose-400" />
            Burnout Risk Trend (Weekly)
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" stroke="#64748b" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 50]} stroke="#64748b" tick={{ fontSize: 12 }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }} />
                <Line type="monotone" dataKey="burnout" name="Burnout Risk %" stroke="#f43f5e" strokeWidth={3} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Grid 2: Productive Time vs Entertainment & Attendance Trend */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Productive Time vs Entertainment Usage */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
            <Clock className="w-4 h-4 text-brand-400" />
            Productive Study vs Entertainment Time (Hours)
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" stroke="#64748b" tick={{ fontSize: 12 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 12 }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Bar dataKey="productive" name="Productive Study (hrs)" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="entertainment" name="Entertainment (hrs)" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Monthly Comparison & Assignment Completion */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
            <Calendar className="w-4 h-4 text-purple-400" />
            Monthly Comparison & Assignment %
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="week" stroke="#64748b" tick={{ fontSize: 12 }} />
                <YAxis domain={[60, 100]} stroke="#64748b" tick={{ fontSize: 12 }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Line type="monotone" dataKey="focus" name="Focus Score Avg" stroke="#10b981" strokeWidth={2} />
                <Line type="monotone" dataKey="assignments" name="Assignment %" stroke="#8b5cf6" strokeWidth={2} strokeDasharray="4 4" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
