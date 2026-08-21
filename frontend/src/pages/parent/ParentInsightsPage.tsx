import React, { useEffect, useState } from 'react';
import { Brain, Lightbulb, Sparkles, AlertCircle, CheckCircle2 } from 'lucide-react';
import { ParentService } from '../../services/parentService';
import { AIInsights } from '../../types';

export const ParentInsightsPage: React.FC = () => {
  const [data, setData] = useState<AIInsights | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    ParentService.getAIInsights().then(res => {
      setData(res);
      setLoading(false);
    });
  }, []);

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">StudIQ AI Intelligence Insights</h1>
          <p className="text-xs text-slate-400 mt-1">Autonomous behavioral pattern synthesis & tailored parental recommendations</p>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5 font-mono">
          <Sparkles className="w-3.5 h-3.5" /> AI Engine Active
        </span>
      </div>

      {/* Insights List */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800">
        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <Brain className="w-5 h-5 text-indigo-400" /> Key Behavioral Patterns Detected
        </h2>
        <div className="space-y-3">
          {data.insights.map((ins) => (
            <div key={ins.id} className="p-4 rounded-xl glass-panel border border-slate-800 flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 mt-0.5" />
                <div>
                  <p className="text-xs font-semibold text-slate-100">{ins.message}</p>
                  {ins.metric && <span className="inline-block mt-1 text-[10px] font-mono text-brand-400">{ins.metric}</span>}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800">
        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-amber-400" /> Actionable Recommendations
        </h2>
        <div className="space-y-3">
          {data.recommendations.map((rec) => (
            <div key={rec.id} className="p-4 rounded-xl glass-panel border border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="w-2 h-2 rounded-full bg-amber-400" />
                <p className="text-xs text-slate-200">{rec.message}</p>
              </div>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                {rec.category}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
