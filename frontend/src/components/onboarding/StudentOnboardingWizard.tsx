import React, { useState } from 'react';
import {
  ShieldCheck,
  Eye,
  Lock,
  CheckCircle2,
  XCircle,
  Mail,
  ArrowRight,
  BrainCircuit,
  Sparkles,
  Activity,
  UserCheck
} from 'lucide-react';

interface StudentOnboardingWizardProps {
  onComplete: () => void;
}

export const StudentOnboardingWizard: React.FC<StudentOnboardingWizardProps> = ({ onComplete }) => {
  const [step, setStep] = useState<1 | 2 | 3 | 4 | 5 | 6>(1);
  const [parentEmail, setParentEmail] = useState('parent.mercer@gmail.com');
  const [isSending, setIsSending] = useState(false);

  const handleSendConsent = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSending(true);
    setTimeout(() => {
      setIsSending(false);
      setStep(4);
    }, 800);
  };

  const handleFinishOnboarding = () => {
    localStorage.setItem('studiq_monitoring_enabled', 'true');
    localStorage.setItem('studiq_parent_email', parentEmail);
    onComplete();
  };

  return (
    <div className="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-50 flex items-center justify-center p-4 overflow-y-auto font-sans">
      <div className="max-w-2xl w-full glass-card rounded-2xl border border-slate-800 p-6 md:p-8 shadow-2xl space-y-6 relative my-auto">
        {/* Progress Bar Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-emerald-500 flex items-center justify-center text-white font-bold shadow-md">
              <BrainCircuit className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">First-Time Student Onboarding</h2>
              <p className="text-[11px] text-slate-400 font-mono">Step {step} of 6 • Mandatory Setup</p>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            {[1, 2, 3, 4, 5, 6].map((s) => (
              <div
                key={s}
                className={`w-5 h-2 rounded-full transition-all ${
                  step >= s ? 'bg-brand-500' : 'bg-slate-800'
                }`}
              />
            ))}
          </div>
        </div>

        {/* STEP 1: Welcome Screen */}
        {step === 1 && (
          <div className="space-y-5 animate-in fade-in duration-200">
            <div className="text-center py-2 space-y-2">
              <div className="w-14 h-14 rounded-2xl bg-brand-500/10 border border-brand-500/20 text-brand-400 flex items-center justify-center mx-auto mb-3">
                <BrainCircuit className="w-7 h-7" />
              </div>
              <h3 className="text-xl font-black text-white">Welcome to StudIQ</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
                StudIQ is an AI-powered Digital Behaviour Intelligence Platform designed to predict student burnout before it impacts academic performance.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
                <Activity className="w-5 h-5 text-emerald-400 mb-1" />
                <h4 className="font-bold text-slate-200">Continuous Monitoring</h4>
                <p className="text-slate-400 text-[11px] leading-relaxed">
                  Passively classifies desktop window titles and educational vs entertainment usage.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
                <Sparkles className="w-5 h-5 text-brand-400 mb-1" />
                <h4 className="font-bold text-slate-200">Predictive Burnout Engine</h4>
                <p className="text-slate-400 text-[11px] leading-relaxed">
                  Identifies fatigue probability and delivers timely, empathetic study recommendations.
                </p>
              </div>
            </div>

            <button
              onClick={() => setStep(2)}
              className="w-full bg-brand-600 hover:bg-brand-500 text-white font-bold py-3 rounded-xl text-xs flex items-center justify-center gap-2 transition shadow-lg shadow-brand-500/20"
            >
              Continue to Privacy Policy <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* STEP 2: Privacy Policy */}
        {step === 2 && (
          <div className="space-y-5 animate-in fade-in duration-200">
            <div>
              <h3 className="text-base font-bold text-white mb-1">Privacy Policy & Data Security</h3>
              <p className="text-xs text-slate-400">Read how StudIQ protects your identity with Zero-Knowledge encryption.</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3 text-xs text-slate-300 leading-relaxed max-h-48 overflow-y-auto font-sans">
              <p>
                <strong className="text-white block mb-1">1. Anonymized Telemetry Processing</strong>
                StudIQ only processes high-level metadata (application name, browser domain category, session length) to calculate focus scores. No keylogging or personal data is collected.
              </p>
              <p>
                <strong className="text-white block mb-1">2. Parental & Mentor Visibility Controls</strong>
                Parents and faculty mentors receive aggregate wellness indicators to support student wellbeing. Private personal files remain strictly invisible to all parties.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setStep(1)}
                className="px-4 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-xs font-semibold text-slate-400"
              >
                Back
              </button>
              <button
                onClick={() => setStep(3)}
                className="flex-1 bg-brand-600 hover:bg-brand-500 text-white font-bold py-3 rounded-xl text-xs flex items-center justify-center gap-2 transition"
              >
                Accept Privacy Policy & Proceed <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* STEP 3: Parent Consent Request */}
        {step === 3 && (
          <form onSubmit={handleSendConsent} className="space-y-5 animate-in fade-in duration-200">
            <div>
              <h3 className="text-base font-bold text-white mb-1">Parent / Guardian Authorization Request</h3>
              <p className="text-xs text-slate-400">
                Enter your parent or guardian's email address to dispatch the required consent request.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
              <label className="block text-xs font-semibold text-slate-300">
                Parent / Guardian Email
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3.5 top-3 text-slate-500" />
                <input
                  type="email"
                  required
                  value={parentEmail}
                  onChange={(e) => setParentEmail(e.target.value)}
                  placeholder="parent.mercer@gmail.com"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
                />
              </div>
              <p className="text-[11px] text-slate-500 font-mono">
                An authorization token link will be dispatched to this guardian address.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setStep(2)}
                className="px-4 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-xs font-semibold text-slate-400"
              >
                Back
              </button>
              <button
                type="submit"
                disabled={isSending}
                className="flex-1 bg-brand-600 hover:bg-brand-500 text-white font-bold py-3 rounded-xl text-xs flex items-center justify-center gap-2 transition"
              >
                {isSending ? 'Dispatching Request...' : 'Send Parent Approval Request'}
              </button>
            </div>
          </form>
        )}

        {/* STEP 4: Parent Approval Confirmation */}
        {step === 4 && (
          <div className="space-y-6 text-center animate-in fade-in duration-200 py-2">
            <div className="w-14 h-14 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center justify-center mx-auto">
              <UserCheck className="w-7 h-7" />
            </div>

            <div>
              <h3 className="text-lg font-bold text-white mb-1">Parent Approval Received</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Guardian consent verified for <span className="font-mono text-emerald-400">{parentEmail}</span>. Proceed to review device monitoring permissions.
              </p>
            </div>

            <button
              onClick={() => setStep(5)}
              className="w-full bg-brand-600 hover:bg-brand-500 text-white font-bold py-3 rounded-xl text-xs flex items-center justify-center gap-2 transition"
            >
              Review Monitoring Permission Screen <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* STEP 5: Monitoring Permission Screen (Allowed vs NOT Allowed) */}
        {step === 5 && (
          <div className="space-y-5 animate-in fade-in duration-200">
            <div>
              <h3 className="text-base font-bold text-white mb-1">Monitoring Permission Scope</h3>
              <p className="text-xs text-slate-400">Review exact permissions allowed vs. strictly excluded from monitoring.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              {/* ALLOWED */}
              <div className="p-4 rounded-xl bg-slate-900/90 border border-emerald-500/20 space-y-3">
                <div className="flex items-center gap-2 font-bold text-emerald-400 border-b border-slate-800 pb-2 font-mono">
                  <CheckCircle2 className="w-4 h-4" /> ALLOWED PERMISSIONS
                </div>
                <ul className="space-y-2 text-slate-300 text-[11px]">
                  <li className="flex items-center gap-2">✓ Running Applications</li>
                  <li className="flex items-center gap-2">✓ Window Title</li>
                  <li className="flex items-center gap-2">✓ Browser URL / Domain</li>
                  <li className="flex items-center gap-2">✓ Time Spent</li>
                  <li className="flex items-center gap-2">✓ Activity Category</li>
                </ul>
              </div>

              {/* NOT ALLOWED */}
              <div className="p-4 rounded-xl bg-slate-900/90 border border-rose-500/20 space-y-3">
                <div className="flex items-center gap-2 font-bold text-rose-400 border-b border-slate-800 pb-2 font-mono">
                  <XCircle className="w-4 h-4" /> NOT ALLOWED (EXCLUDED)
                </div>
                <ul className="space-y-2 text-slate-400 text-[11px]">
                  <li className="flex items-center gap-2 text-slate-400 line-through">✗ Gallery & Photos</li>
                  <li className="flex items-center gap-2 text-slate-400 line-through">✗ Passwords</li>
                  <li className="flex items-center gap-2 text-slate-400 line-through">✗ Bank Accounts</li>
                  <li className="flex items-center gap-2 text-slate-400 line-through">✗ Private Files</li>
                  <li className="flex items-center gap-2 text-slate-400 line-through">✗ Messages</li>
                </ul>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setStep(4)}
                className="px-4 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-xs font-semibold text-slate-400"
              >
                Back
              </button>
              <button
                onClick={() => setStep(6)}
                className="flex-1 bg-brand-600 hover:bg-brand-500 text-white font-bold py-3 rounded-xl text-xs flex items-center justify-center gap-2 transition"
              >
                Grant Permissions & Activate Monitoring <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* STEP 6: Monitoring Enabled */}
        {step === 6 && (
          <div className="space-y-6 text-center animate-in fade-in zoom-in-95 duration-200 py-4">
            <div className="w-16 h-16 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center justify-center mx-auto">
              <ShieldCheck className="w-8 h-8" />
            </div>

            <div>
              <h3 className="text-lg font-bold text-white mb-1">Monitoring Enabled & Operational</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Permissions granted and telemetry stream active. You may now enter your StudIQ Student Dashboard.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-left text-xs space-y-2">
              <div className="flex items-center justify-between text-slate-300 font-semibold border-b border-slate-800 pb-2">
                <span>Monitoring Status</span>
                <span className="text-emerald-400 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" /> Active & Monitoring
                </span>
              </div>
              <div className="flex items-center justify-between text-slate-400 text-[11px]">
                <span>App & Web Telemetry</span>
                <span className="font-mono text-slate-200">Enabled</span>
              </div>
              <div className="flex items-center justify-between text-slate-400 text-[11px]">
                <span>AI Burnout Predictor</span>
                <span className="font-mono text-slate-200">Online v2.4</span>
              </div>
            </div>

            <button
              onClick={handleFinishOnboarding}
              className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-xl text-xs shadow-lg shadow-emerald-500/20 transition"
            >
              Enter StudIQ Student Dashboard →
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
