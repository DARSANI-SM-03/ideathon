import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export const ServerErrorPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center p-6">
      <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mb-4">
        <AlertTriangle className="w-10 h-10 text-amber-400" />
      </div>
      <h1 className="text-4xl font-extrabold text-slate-100 mb-2">500 - Server Exception</h1>
      <p className="text-sm text-slate-400 max-w-md mb-6">
        An internal server exception occurred. StudIQ offline fallback dataset is currently active.
      </p>
      <button
        onClick={() => window.location.reload()}
        className="bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs py-2.5 px-5 rounded-xl flex items-center gap-2 transition"
      >
        <RefreshCw className="w-4 h-4" /> Reload System
      </button>
    </div>
  );
};
