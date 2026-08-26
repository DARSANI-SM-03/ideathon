import React from 'react';
import {
  Activity,
  Laptop,
  GraduationCap,
  Code,
  Sparkles,
  Clock,
  ShieldCheck,
  Zap,
  Radio,
  Tv,
  Brain,
  AlertCircle
} from 'lucide-react';

export interface CurrentlyActiveData {
  is_active?: boolean;
  active_activity_status?: string;
  application?: string;
  current_application?: string;
  domain?: string;
  page_title?: string;
  window_title?: string;
  website_url?: string;
  category?: string;
  subcategory?: string;
  confidence?: number;
  confidence_percent?: string;
  productivity_score?: number;
  productivity_percent?: string;
  focus_score?: number;
  focus_percent?: string;
  distraction_score?: number;
  distraction_percent?: string;
  active_duration_seconds?: number;
  active_duration_formatted?: string;
  agent_connected?: boolean;
}

interface Props {
  data: CurrentlyActiveData | null;
  title?: string;
  className?: string;
}

export const CurrentlyActiveCard: React.FC<Props> = ({
  data,
  title = "CURRENTLY ACTIVE",
  className = ""
}) => {
  const is_active = Boolean(data?.is_active && data?.agent_connected !== false);
  const app = data?.application || data?.current_application || 'Desktop Agent';
  const page_title = data?.page_title || data?.window_title || 'Active Web Session';
  const domain = data?.domain && data.domain !== 'N/A' ? data.domain : '';
  const category = data?.category || 'Education';
  const subcategory = data?.subcategory || 'General';
  const confidencePct = data?.confidence_percent || `${Math.round((data?.confidence || 0.95) * 100)}%`;
  const focusPct = data?.focus_percent || `${Math.round((data?.focus_score || 0.90) * 100)}%`;
  const prodPct = data?.productivity_percent || `${Math.round((data?.productivity_score || 0.95) * 100)}%`;
  const durationFmt = data?.active_duration_formatted || '0s';

  const getCategoryColor = (cat: string) => {
    const c = cat.toLowerCase();
    if (c.includes('education') || c.includes('academic')) return 'from-emerald-500/20 to-teal-500/20 text-emerald-400 border-emerald-500/30';
    if (c.includes('coding') || c.includes('technical') || c.includes('development')) return 'from-cyan-500/20 to-blue-500/20 text-cyan-400 border-cyan-500/30';
    if (c.includes('productivity') || c.includes('productive')) return 'from-purple-500/20 to-indigo-500/20 text-purple-400 border-purple-500/30';
    if (c.includes('social')) return 'from-pink-500/20 to-rose-500/20 text-pink-400 border-pink-500/30';
    if (c.includes('entertainment') || c.includes('gaming')) return 'from-amber-500/20 to-orange-500/20 text-amber-400 border-amber-500/30';
    return 'from-slate-500/20 to-slate-700/20 text-slate-300 border-slate-500/30';
  };

  const getAppIcon = (app_str: string, cat_str: string) => {
    const a = app_str.toLowerCase();
    if (a.includes('youtube')) return <Tv className="w-6 h-6 text-red-400" />;
    if (a.includes('code') || a.includes('visual studio') || a.includes('pycharm')) return <Code className="w-6 h-6 text-cyan-400" />;
    if (a.includes('chatgpt')) return <Sparkles className="w-6 h-6 text-emerald-400" />;
    if (cat_str.toLowerCase().includes('education')) return <GraduationCap className="w-6 h-6 text-emerald-400" />;
    return <Laptop className="w-6 h-6 text-indigo-400" />;
  };

  return (
    <div className={`relative overflow-hidden rounded-2xl bg-slate-900/90 border border-slate-800 p-6 shadow-xl backdrop-blur-xl transition-all duration-300 ${className}`}>
      {/* Glow Ambient Effect */}
      <div className={`absolute -top-24 -right-24 w-48 h-48 rounded-full blur-3xl opacity-25 ${is_active ? 'bg-emerald-500' : 'bg-slate-600'}`} />

      {/* Card Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2.5">
          <span className="relative flex h-3 w-3">
            {is_active && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />}
            <span className={`relative inline-flex rounded-full h-3 w-3 ${is_active ? 'bg-emerald-500' : 'bg-slate-500'}`} />
          </span>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">{title}</h3>
        </div>
        {is_active ? (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Radio className="w-3 h-3 mr-1 animate-pulse" /> LIVE STREAMING
          </span>
        ) : (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700">
            IDLE / INACTIVE
          </span>
        )}
      </div>

      {!is_active ? (
        <div className="py-6 text-center space-y-2">
          <div className="w-12 h-12 rounded-full bg-slate-800/80 border border-slate-700/60 flex items-center justify-center mx-auto text-slate-400 mb-3">
            <Activity className="w-6 h-6" />
          </div>
          <h4 className="text-base font-semibold text-slate-200">No active activity detected</h4>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Student desktop monitoring agent is idle or awaiting new foreground activity.
          </p>
        </div>
      ) : (
        <div className="space-y-5">
          {/* Main Activity Info */}
          <div className="flex items-start space-x-4">
            <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/60 shadow-inner shrink-0">
              {getAppIcon(app, category)}
            </div>

            <div className="flex-1 min-w-0">
              <h4 className="text-lg font-bold text-slate-100 truncate tracking-tight" title={page_title}>
                {page_title}
              </h4>
              <p className="text-xs font-medium text-slate-400 truncate mt-0.5">
                {domain ? `${domain} · ` : ''}{app}
              </p>

              {/* Taxonomy Pill */}
              <div className={`mt-2.5 inline-flex items-center px-3 py-1 rounded-lg text-xs font-semibold bg-gradient-to-r border shadow-sm ${getCategoryColor(category)}`}>
                <Sparkles className="w-3.5 h-3.5 mr-1.5 opacity-80" />
                {category} <span className="mx-1 text-slate-500">·</span> {subcategory}
              </div>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 border-t border-slate-800/80">
            <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-800/80">
              <div className="flex items-center text-slate-400 text-xs font-medium mb-1">
                <Clock className="w-3.5 h-3.5 mr-1 text-indigo-400" /> Active Time
              </div>
              <div className="text-base font-bold text-slate-100">{durationFmt}</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-800/80">
              <div className="flex items-center text-slate-400 text-xs font-medium mb-1">
                <Brain className="w-3.5 h-3.5 mr-1 text-emerald-400" /> Focus Index
              </div>
              <div className="text-base font-bold text-emerald-400">{focusPct}</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-800/80">
              <div className="flex items-center text-slate-400 text-xs font-medium mb-1">
                <Zap className="w-3.5 h-3.5 mr-1 text-cyan-400" /> Productivity
              </div>
              <div className="text-base font-bold text-cyan-400">{prodPct}</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-800/80">
              <div className="flex items-center text-slate-400 text-xs font-medium mb-1">
                <ShieldCheck className="w-3.5 h-3.5 mr-1 text-purple-400" /> AI Confidence
              </div>
              <div className="text-base font-bold text-purple-400">{confidencePct}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
