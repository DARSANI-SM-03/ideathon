import React from 'react';
import { Award, Flame, CheckCircle2, ShieldCheck, Sun, Zap } from 'lucide-react';

export const AchievementsGrid: React.FC = () => {
  const achievements = [
    { id: 1, title: '7 Day Focus Streak', desc: 'Maintained >80 Focus Score for 7 consecutive days', icon: Flame, color: 'text-amber-400 bg-amber-500/10 border-amber-500/30', unlocked: true },
    { id: 2, title: 'Assignment Champion', desc: 'Submitted all 5 course assignments on time', icon: CheckCircle2, color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30', unlocked: true },
    { id: 3, title: 'No Distraction Day', desc: 'Zero entertainment apps opened during Study Mode', icon: ShieldCheck, color: 'text-brand-400 bg-brand-500/10 border-brand-500/30', unlocked: true },
    { id: 4, title: 'Productive Week', desc: 'Completed over 30 hours of deep coding & research', icon: Zap, color: 'text-purple-400 bg-purple-500/10 border-purple-500/30', unlocked: true },
    { id: 5, title: 'Early Bird', desc: 'Completed 2 study sessions before 09:00 AM', icon: Sun, color: 'text-amber-400 bg-amber-500/10 border-amber-500/30', unlocked: false },
    { id: 6, title: 'Consistency Badge', desc: 'Maintained Low Burnout Risk for 30 days', icon: Award, color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30', unlocked: true }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Award className="w-6 h-6 text-brand-400" />
            Personal Achievements & Milestones
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Private badging system tracking study consistency and healthy habits (No public leaderboards).
          </p>
        </div>

        <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-xl border border-emerald-500/20 font-bold">
          5 / 6 Badges Unlocked
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {achievements.map((a) => {
          const Icon = a.icon;
          return (
            <div
              key={a.id}
              className={`glass-card rounded-2xl p-5 border flex items-start gap-4 transition ${
                a.unlocked ? 'border-slate-800' : 'border-slate-800/40 opacity-50'
              }`}
            >
              <div className={`p-3 rounded-xl border ${a.color}`}>
                <Icon className="w-6 h-6" />
              </div>

              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-bold text-slate-100">{a.title}</h3>
                  {a.unlocked && <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.5 rounded font-mono">UNLOCKED</span>}
                </div>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">{a.desc}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
