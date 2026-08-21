import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FileQuestion, ArrowLeft } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center p-6">
      <div className="w-16 h-16 rounded-2xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center mb-4">
        <FileQuestion className="w-10 h-10 text-brand-400" />
      </div>
      <h1 className="text-4xl font-extrabold text-slate-100 mb-2">404 - Page Not Found</h1>
      <p className="text-sm text-slate-400 max-w-md mb-6">
        The academic intelligence view or report URL you requested could not be found.
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
