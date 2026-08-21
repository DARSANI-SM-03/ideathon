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
