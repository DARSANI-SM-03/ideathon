import React, { useState } from 'react';
import { Send, UserCheck, ShieldCheck } from 'lucide-react';

export const MentorMessagesPage: React.FC = () => {
  const [messages, setMessages] = useState([
    { id: '1', sender: 'Alex Mercer (Student)', text: 'Dr. Vance, could I schedule a 10-min meeting on Tuesday regarding my CS301 project?', time: '09:15 AM', isMe: false },
    { id: '2', sender: 'Dr. Robert Vance (Mentor)', text: 'Sure Alex! Let us connect at 2:00 PM in my office.', time: '09:25 AM', isMe: true },
  ]);
  const [input, setInput] = useState('');

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setMessages([
      ...messages,
      { id: Date.now().toString(), sender: 'Dr. Robert Vance (Mentor)', text: input, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), isMe: true }
    ]);
    setInput('');
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Mentor Communication Center</h1>
        <p className="text-xs text-slate-400 mt-1">Direct messaging channel with assigned mentees and parents</p>
      </div>

      <div className="glass-card rounded-2xl border border-slate-800 flex flex-col h-[500px] overflow-hidden">
        <div className="p-4 border-b border-slate-800 bg-slate-900/50 flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-brand-500/20 text-brand-400 flex items-center justify-center font-bold">
            AM
          </div>
          <div>
            <h3 className="text-xs font-bold text-white">Alex Mercer</h3>
            <p className="text-[10px] text-slate-400">Computer Science &bull; Semester 4</p>
          </div>
        </div>

        <div className="flex-1 p-4 overflow-y-auto space-y-4">
          {messages.map((m) => (
            <div key={m.id} className={`flex flex-col ${m.isMe ? 'items-end' : 'items-start'}`}>
              <div className={`max-w-md p-3.5 rounded-2xl text-xs ${m.isMe ? 'bg-brand-600 text-white rounded-br-none' : 'glass-panel border border-slate-800 text-slate-200 rounded-bl-none'}`}>
                <p className="font-semibold text-[10px] opacity-70 mb-1">{m.sender}</p>
                <p>{m.text}</p>
              </div>
              <span className="text-[10px] text-slate-500 mt-1 font-mono">{m.time}</span>
            </div>
          ))}
        </div>

        <form onSubmit={handleSend} className="p-3 border-t border-slate-800 bg-slate-900/40 flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message to Alex..."
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
          />
          <button type="submit" className="p-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white">
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
