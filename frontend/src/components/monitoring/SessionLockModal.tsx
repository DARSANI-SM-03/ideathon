import React from 'react';
import { Lock, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { Modal } from '../Modal';

interface SessionLockModalProps {
  isOpen: boolean;
  onAcknowledgeAndResume: () => void;
}

export const SessionLockModal: React.FC<SessionLockModalProps> = ({
  isOpen,
  onAcknowledgeAndResume
}) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={() => {}}
      title="Study Session Locked"
    >
      <div className="space-y-4 py-2 text-center font-sans">
        <div className="w-14 h-14 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-400 flex items-center justify-center mx-auto">
          <Lock className="w-7 h-7" />
        </div>

        <div className="space-y-1">
          <h3 className="text-base font-bold text-white">Entertainment Limit Repeatedly Ignored</h3>
          <p className="text-xs text-slate-300 max-w-sm mx-auto leading-relaxed">
            You ignored 6 consecutive usage warnings. Your active study session has been temporarily locked.
          </p>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-900 border border-rose-500/20 text-left text-xs space-y-1.5">
          <div className="flex items-center gap-2 text-rose-400 font-semibold font-mono text-[11px]">
            <ShieldAlert className="w-4 h-4" /> AUTOMATED ACTION DISPATCHED
          </div>
          <p className="text-slate-400 text-[11px] leading-relaxed">
            A guardian notification has been dispatched to your registered parent email (<span className="text-slate-200 font-mono">parent.mercer@gmail.com</span>). Faculty mentor was <i>not</i> notified immediately.
          </p>
        </div>

        <button
          onClick={onAcknowledgeAndResume}
          className="w-full bg-brand-600 hover:bg-brand-500 text-white font-bold py-3 rounded-xl text-xs flex items-center justify-center gap-2 transition shadow-lg shadow-brand-500/20"
        >
          <CheckCircle2 className="w-4 h-4" /> Acknowledge & Return to Study Session
        </button>
      </div>
    </Modal>
  );
};
