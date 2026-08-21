import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, ArrowLeft } from 'lucide-react';

export const ForbiddenPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center p-6">
      <div className="w-16 h-16 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center mb-4">
        <ShieldAlert className="w-10 h-10 text-rose-400" />
      </div>
      <h1 className="text-4xl font-extrabold text-slate-100 mb-2">403 - Access Forbidden</h1>
      <p className="text-sm text-slate-400 max-w-md mb-6">
        Your current role is not authorized to access this institutional management portal.
      </p>
      <button
        onClick={() => navigate('/')}
        className="bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs py-2.5 px-5 rounded-xl flex items-center gap-2 transition"
      >
        <ArrowLeft className="w-4 h-4" /> Return to Dashboard
      </button>
    </div>
  );
};
