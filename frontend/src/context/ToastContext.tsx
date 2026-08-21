import React, { createContext, useContext, useState } from 'react';
import { CheckCircle2, AlertTriangle, Info, X } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastContextType {
  showToast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = (message: string, type: ToastType = 'success') => {
    const id = Date.now().toString();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      removeToast(id);
    }, 4000);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {/* Toast Notification Floating Container */}
      <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
        {toasts.map((toast) => {
          const iconMap = {
            success: <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />,
            error: <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0" />,
            warning: <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0" />,
            info: <Info className="w-5 h-5 text-brand-400 flex-shrink-0" />
          };

          const styleMap = {
            success: 'bg-slate-900/95 border-emerald-500/30 text-emerald-200',
            error: 'bg-slate-900/95 border-rose-500/30 text-rose-200',
            warning: 'bg-slate-900/95 border-amber-500/30 text-amber-200',
            info: 'bg-slate-900/95 border-brand-500/30 text-brand-200'
          };

          return (
            <div
              key={toast.id}
              className={`pointer-events-auto p-4 rounded-xl border backdrop-blur-md shadow-2xl flex items-center justify-between gap-3 animate-in slide-in-from-right duration-300 ${styleMap[toast.type]}`}
            >
              <div className="flex items-center gap-2.5">
                {iconMap[toast.type]}
                <span className="text-xs font-medium">{toast.message}</span>
              </div>
              <button
                onClick={() => removeToast(toast.id)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-200 transition"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) throw new Error('useToast must be used within ToastProvider');
  return context;
};
