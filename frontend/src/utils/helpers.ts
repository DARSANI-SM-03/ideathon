import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// ============================================================
// DATE & TIME
// ============================================================

export function formatRelativeTime(isoDate: string): string {
  if (!isoDate) return '';
  const date = new Date(isoDate);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days === 1) return 'Yesterday';
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
}

export function formatDate(isoDate: string): string {
  if (!isoDate) return '';
  return new Date(isoDate).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

export function formatDateTime(isoDate: string): string {
  if (!isoDate) return '';
  return new Date(isoDate).toLocaleString('en-IN', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}

// ============================================================
// RISK / STATUS COLORS
// ============================================================

export function getBurnoutRiskConfig(risk: string) {
  const configs: Record<string, { label: string; className: string; color: string; bgColor: string; dot: string }> = {
    critical: {
      label: 'Critical',
      className: 'risk-critical',
      color: '#f43f5e',
      bgColor: 'rgba(244, 63, 94, 0.1)',
      dot: 'bg-rose-500',
    },
    high: {
      label: 'High',
      className: 'risk-high',
      color: '#f97316',
      bgColor: 'rgba(249, 115, 22, 0.1)',
      dot: 'bg-orange-500',
    },
    medium: {
      label: 'Medium',
      className: 'risk-medium',
      color: '#f59e0b',
      bgColor: 'rgba(245, 158, 11, 0.1)',
      dot: 'bg-amber-500',
    },
    low: {
      label: 'Low',
      className: 'risk-low',
      color: '#10b981',
      bgColor: 'rgba(16, 185, 129, 0.1)',
      dot: 'bg-emerald-500',
    },
  };
  return configs[risk.toLowerCase()] || configs.low;
}

export function getStatusConfig(status: string) {
  const configs: Record<string, { label: string; className: string; color: string; textClass: string }> = {
    online: {
      label: 'Online',
      className: 'status-online',
      color: '#10b981',
      textClass: 'text-emerald-400',
    },
    studying: {
      label: 'Studying',
      className: 'status-studying',
      color: '#3b82f6',
      textClass: 'text-blue-400',
    },
    entertainment: {
      label: 'Entertainment',
      className: 'status-entertainment',
      color: '#f59e0b',
      textClass: 'text-amber-400',
    },
    offline: {
      label: 'Offline',
      className: 'status-offline',
      color: '#94a3b8',
      textClass: 'text-slate-400',
    },
  };
  return configs[status.toLowerCase()] || configs.offline;
}

export function getPriorityConfig(priority: string) {
  const configs: Record<string, { label: string; color: string; className: string }> = {
    urgent: { label: 'Urgent', color: '#f43f5e', className: 'risk-critical' },
    high: { label: 'High', color: '#f97316', className: 'risk-high' },
    medium: { label: 'Medium', color: '#f59e0b', className: 'risk-medium' },
    low: { label: 'Low', color: '#10b981', className: 'risk-low' },
  };
  return configs[priority.toLowerCase()] || configs.low;
}

export function formatScore(score: number): string {
  return `${Math.round(score)}`;
}

export function formatPercentage(value: number): string {
  return `${Math.round(value)}%`;
}

export function formatCGPA(cgpa: number): string {
  return cgpa.toFixed(1);
}

export function getScoreColor(score: number, inverse = false): string {
  if (inverse) {
    if (score >= 80) return '#f43f5e';
    if (score >= 60) return '#f97316';
    if (score >= 40) return '#f59e0b';
    return '#10b981';
  } else {
    if (score >= 75) return '#10b981';
    if (score >= 55) return '#3b82f6';
    if (score >= 35) return '#f59e0b';
    return '#f43f5e';
  }
}

export function getInitials(name: string): string {
  if (!name) return 'U';
  return name
    .split(' ')
    .slice(0, 2)
    .map((n) => n[0])
    .join('')
    .toUpperCase();
}

export function getAvatarColor(name: string): string {
  if (!name) return 'from-violet-500 to-purple-600';
  const colors = [
    'from-violet-500 to-purple-600',
    'from-blue-500 to-indigo-600',
    'from-emerald-500 to-teal-600',
    'from-rose-500 to-pink-600',
    'from-amber-500 to-orange-600',
    'from-cyan-500 to-sky-600',
  ];
  const idx = name.charCodeAt(0) % colors.length;
  return colors[idx];
}

export const PRIORITY_CATEGORY_LABELS: Record<string, string> = {
  critical_burnout: '🔴 Critical Burnout',
  high_burnout: '🟠 High Burnout',
  low_focus: '🟡 Low Focus',
  low_attendance: '📉 Low Attendance',
  pending_assignments: '📋 Pending Assignments',
  inactive: '💤 Inactive',
};

export const DEPARTMENTS = [
  'Computer Science',
  'Electronics',
  'Mechanical',
  'Civil',
  'MBA',
  'Biotechnology',
  'Physics',
];

export const SEMESTERS = [1, 2, 3, 4, 5, 6, 7, 8];

// ============================================================
// APPLICATION NAME FORMATTING
// ============================================================

export function getReadableAppName(rawApp?: string): string {
  if (!rawApp) return 'No active application';
  const clean = rawApp.trim().toLowerCase();

  const appMap: Record<string, string> = {
    'chrome.exe': 'Google Chrome',
    'chrome': 'Google Chrome',
    'msedge.exe': 'Microsoft Edge',
    'msedge': 'Microsoft Edge',
    'firefox.exe': 'Mozilla Firefox',
    'firefox': 'Mozilla Firefox',
    'brave.exe': 'Brave Browser',
    'brave': 'Brave Browser',
    'opera.exe': 'Opera Browser',
    'opera': 'Opera Browser',
    'code.exe': 'Visual Studio Code',
    'code': 'Visual Studio Code',
    'antigravity ide.exe': 'Antigravity IDE',
    'antigravity ide': 'Antigravity IDE',
    'antigravity': 'Antigravity IDE',
    'pycharm64.exe': 'PyCharm',
    'pycharm': 'PyCharm',
    'idea64.exe': 'IntelliJ IDEA',
    'intellij': 'IntelliJ IDEA',
    'eclipse.exe': 'Eclipse',
    'eclipse': 'Eclipse',
    'windowsterminal.exe': 'Windows Terminal',
    'windowsterminal': 'Windows Terminal',
    'cmd.exe': 'Command Prompt',
    'cmd': 'Command Prompt',
    'powershell.exe': 'PowerShell',
    'powershell': 'PowerShell',
    'spotify.exe': 'Spotify',
    'spotify': 'Spotify',
    'vlc.exe': 'VLC Media Player',
    'vlc': 'VLC Media Player',
    'netflix.exe': 'Netflix',
    'netflix': 'Netflix',
    'notion.exe': 'Notion',
    'notion': 'Notion',
    'obsidian.exe': 'Obsidian',
    'obsidian': 'Obsidian',
    'onenote.exe': 'Microsoft OneNote',
    'onenote': 'Microsoft OneNote',
    'word.exe': 'Microsoft Word',
    'winword.exe': 'Microsoft Word',
    'excel.exe': 'Microsoft Excel',
    'powerpnt.exe': 'Microsoft PowerPoint',
    'teams.exe': 'Microsoft Teams',
    'zoom.exe': 'Zoom',
    'slack.exe': 'Slack',
    'slack': 'Slack',
    'discord.exe': 'Discord',
    'discord': 'Discord',
    'figma.exe': 'Figma',
    'figma': 'Figma',
    'canva.exe': 'Canva',
    'canva': 'Canva',
    'postman.exe': 'Postman',
    'postman': 'Postman',
    'docker desktop.exe': 'Docker Desktop',
    'docker.exe': 'Docker',
    'docker': 'Docker',
    'gitkraken.exe': 'GitKraken',
    'gitkraken': 'GitKraken',
    'github.exe': 'GitHub Desktop',
    'github desktop': 'GitHub Desktop',
    'explorer.exe': 'File Explorer',
    'explorer': 'File Explorer',
    'taskmgr.exe': 'Task Manager',
    'taskmgr': 'Task Manager',
    'systemsettings.exe': 'Windows Settings',
    'settings': 'Windows Settings',
    'calc.exe': 'Calculator',
    'calculator': 'Calculator',
    'notepad.exe': 'Notepad',
    'notepad': 'Notepad',
    'mspaint.exe': 'Paint',
    'paint': 'Paint'
  };

  if (appMap[clean]) {
    return appMap[clean];
  }

  let name = rawApp.replace(/\.exe$/i, '').trim();
  if (!name) return 'No active application';
  return name.charAt(0).toUpperCase() + name.slice(1);
}
