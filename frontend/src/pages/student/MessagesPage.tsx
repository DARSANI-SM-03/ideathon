import React from 'react';
import { MessageCenter } from '../../components/chat/MessageCenter';

export const MessagesPage: React.FC = () => {
  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 mb-1">StudIQ Message Center</h1>
        <p className="text-xs text-slate-400">Encrypted communication channel between Student, Parent, and Academic Mentor.</p>
      </div>

      <MessageCenter />
    </div>
  );
};
