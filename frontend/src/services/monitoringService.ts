export type ActivityCategory =
  | 'Educational'
  | 'Productive'
  | 'Entertainment'
  | 'Gaming'
  | 'Utilities'
  | 'Unknown';

export type MonitoringStatus = 'Active' | 'Idle' | 'Disabled';

export type FocusScoreLevel = 'Excellent' | 'Good' | 'Average' | 'Low' | 'Critical';

export interface TelemetryPing {
  appName: string;
  windowTitle: string;
  websiteUrl?: string;
  timestamp: string;
  durationSeconds: number;
}

export interface ClassifiedTelemetry extends TelemetryPing {
  category: ActivityCategory;
  focusScore: number;
  burnoutRisk: number;
  aiExplanation: string;
  recommendation: string;
}

export interface MonitoringSessionStats {
  status: MonitoringStatus;
  currentApp: string;
  currentTitle: string;
  currentUrl: string;
  currentCategory: ActivityCategory;
  sessionMins: number;
  productiveMins: number;
  educationalMins: number;
  entertainmentMins: number;
  gamingMins: number;
  idleMins: number;
  focusScore: number;
  focusLevel: FocusScoreLevel;
  burnoutRisk: number;
  ignoredWarningCount: number;
  isSessionLocked: boolean;
}

// Default classification rules (easily configurable)
const APP_RULES: Record<string, ActivityCategory> = {
  'code.exe': 'Productive',
  'visual studio code': 'Productive',
  'vs code': 'Productive',
  'pycharm': 'Productive',
  'pycharm.exe': 'Productive',
  'google classroom': 'Educational',
  'coursera': 'Educational',
  'leetcode': 'Educational',
  'figma': 'Productive',
  'canva': 'Productive',
  'excel': 'Productive',
  'word': 'Productive',
  'powerpoint': 'Productive',
  'notion': 'Productive',
  'instagram': 'Entertainment',
  'netflix': 'Entertainment',
  'hotstar': 'Entertainment',
  'prime video': 'Entertainment',
  'facebook': 'Entertainment',
  'steam': 'Gaming',
  'valorant': 'Gaming',
  'minecraft': 'Gaming',
  'bgmi': 'Gaming',
  'calculator': 'Utilities',
  'settings': 'Utilities',
  'file explorer': 'Utilities'
};

const BROWSER_CONTENT_RULES: Array<{ keyword: string; category: ActivityCategory }> = [
  { keyword: 'dsa lecture', category: 'Educational' },
  { keyword: 'operating system notes', category: 'Educational' },
  { keyword: 'leetcode', category: 'Educational' },
  { keyword: 'arxiv', category: 'Educational' },
  { keyword: 'coursera', category: 'Educational' },
  { keyword: 'docs', category: 'Productive' },
  { keyword: 'github', category: 'Productive' },
  { keyword: 'funny memes', category: 'Entertainment' },
  { keyword: 'netflix', category: 'Entertainment' },
  { keyword: 'gaming stream', category: 'Gaming' },
  { keyword: 'valorant match', category: 'Gaming' }
];

export class MonitoringService {
  private static instance: MonitoringService;
  private status: MonitoringStatus = 'Active';
  private ignoredWarningCount: number = 0;
  private isSessionLocked: boolean = false;

  public static getInstance(): MonitoringService {
    if (!MonitoringService.instance) {
      MonitoringService.instance = new MonitoringService();
    }
    return MonitoringService.instance;
  }

  /**
   * Classifies application and browser title metadata into categories
   */
  public classifyMetadata(appName: string, windowTitle: string, websiteUrl?: string): ActivityCategory {
    const lowerApp = appName.toLowerCase();
    const lowerTitle = windowTitle.toLowerCase();
    const lowerUrl = (websiteUrl || '').toLowerCase();

    // Check URL / browser content keywords first
    for (const rule of BROWSER_CONTENT_RULES) {
      if (lowerTitle.includes(rule.keyword) || lowerUrl.includes(rule.keyword)) {
        return rule.category;
      }
    }

    // Check direct application name rules
    for (const [key, category] of Object.entries(APP_RULES)) {
      if (lowerApp.includes(key)) {
        return category;
      }
    }

    return 'Unknown';
  }

  /**
   * Calculates Focus Score (0 - 100) based on educational, productive, and entertainment balance
   */
  public calculateFocusScore(educationalMins: number, productiveMins: number, entertainmentMins: number, gamingMins: number): { score: number; level: FocusScoreLevel } {
    const positiveTime = educationalMins * 1.2 + productiveMins * 1.0;
    const negativeTime = entertainmentMins * 1.5 + gamingMins * 2.0;

    const netScore = Math.max(0, Math.min(100, Math.round(75 + positiveTime * 0.5 - negativeTime * 0.8)));

    let level: FocusScoreLevel = 'Good';
    if (netScore >= 85) level = 'Excellent';
    else if (netScore >= 70) level = 'Good';
    else if (netScore >= 55) level = 'Average';
    else if (netScore >= 40) level = 'Low';
    else level = 'Critical';

    return { score: netScore, level };
  }

  /**
   * Handles ignored warning increment and determines if session lock is required (on 6th warning)
   */
  public handleIgnoreWarning(): { count: number; shouldLock: boolean; notifyParent: boolean } {
    this.ignoredWarningCount += 1;
    const shouldLock = this.ignoredWarningCount >= 6;
    if (shouldLock) {
      this.isSessionLocked = true;
    }
    return {
      count: this.ignoredWarningCount,
      shouldLock,
      notifyParent: shouldLock || this.ignoredWarningCount >= 3
    };
  }

  public resetWarningCount(): void {
    this.ignoredWarningCount = 0;
    this.isSessionLocked = false;
  }

  public getStatus(): MonitoringStatus {
    return this.status;
  }

  public setStatus(s: MonitoringStatus): void {
    this.status = s;
  }
}

export const LOCAL_BRIDGE_URL = 'http://127.0.0.1:8765';

export const invokeAgentProtocol = (action: 'start' | 'stop' | 'status', params: Record<string, string> = {}) => {
  const query = new URLSearchParams(params).toString();
  const uri = `studiq-agent://${action}${query ? '?' + query : ''}`;
  
  try {
    let iframe = document.getElementById('studiq-protocol-iframe') as HTMLIFrameElement;
    if (!iframe) {
      iframe = document.createElement('iframe');
      iframe.id = 'studiq-protocol-iframe';
      iframe.style.display = 'none';
      document.body.appendChild(iframe);
    }
    iframe.src = uri;
  } catch (e) {
    window.location.href = uri;
  }
};

export interface LocalBridgeStatus {
  bridge_status: string;
  agent_running: boolean;
  agent_pid?: number | null;
}

export class AgentBridgeService {
  public static async checkBridgeStatus(): Promise<LocalBridgeStatus | null> {
    try {
      const res = await fetch(`${LOCAL_BRIDGE_URL}/status`, { signal: AbortSignal.timeout(2000) });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      // Bridge unreachable
    }
    return null;
  }

  public static async downloadInstaller(): Promise<void> {
    try {
      const link = document.createElement('a');
      link.href = `${API_BASE_URL}/monitoring/installer/download`;
      link.download = 'install_studiq_agent.bat';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (e) {
      console.error('Error downloading StudIQ Agent installer:', e);
    }
  }

  public static async pollForBridgeActive(maxTimeoutMs: number = 30000, intervalMs: number = 1500): Promise<LocalBridgeStatus | null> {
    const startTime = Date.now();
    while (Date.now() - startTime < maxTimeoutMs) {
      const status = await this.checkBridgeStatus();
      if (status && status.bridge_status === 'active') {
        return status;
      }
      await new Promise((resolve) => setTimeout(resolve, intervalMs));
    }
    return null;
  }

  public static async startAgent(token: string, backendUrl: string, studentId: number, studentCode: string): Promise<boolean> {
    try {
      const res = await fetch(`${LOCAL_BRIDGE_URL}/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, backend_url: backendUrl, student_id: studentId, student_code: studentCode }),
        signal: AbortSignal.timeout(4000)
      });
      if (res.ok) {
        const data = await res.json();
        return data.status === 'started' || data.status === 'already_running';
      }
    } catch (e) {
      console.warn('Unable to connect to local agent bridge on 127.0.0.1:8765', e);
    }
    return false;
  }

  public static async stopAgent(): Promise<boolean> {
    try {
      const res = await fetch(`${LOCAL_BRIDGE_URL}/stop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(4000)
      });
      if (res.ok) {
        const data = await res.json();
        return data.status === 'stopped';
      }
    } catch (e) {
      console.warn('Unable to connect to local agent bridge on 127.0.0.1:8765', e);
    }
    return false;
  }
}
