import React, { useState } from 'react';
import { Send, User, Check, CheckCheck, MessageSquare } from 'lucide-react';
import { useToast } from '../../context/ToastContext';

interface ChatUser {
  id: string;
  name: string;
  role: string;
  avatar: string;
}

interface Message {
  id: string;
  senderId: string;
  text: string;
  time: string;
  isMe: boolean;
  read: boolean;
}

export const MessageCenter: React.FC<{ defaultChatWith?: string }> = ({ defaultChatWith = 'parent' }) => {
  const { showToast } = useToast();

  const contacts: ChatUser[] = [
    { id: 'parent', name: 'Eleanor Mercer', role: 'Parent', avatar: 'P' },
    { id: 'mentor', name: 'Dr. Robert Vance', role: 'Academic Mentor', avatar: 'M' },
  ];

  const [activeContact, setActiveContact] = useState<ChatUser>(contacts[0]);
  const [inputMsg, setInputMsg] = useState('');

  const [messages, setMessages] = useState<Record<string, Message[]>>({
    parent: [
      { id: 'm1', senderId: 'parent', text: 'Hi Alex, saw your Focus score reached 91 this week! Great job.', time: '10:30 AM', isMe: false, read: true },
      { id: 'm2', senderId: 'me', text: 'Thanks Mom! The Pomodoro timer really helped with ML revision.', time: '10:32 AM', isMe: true, read: true },
    ],
    mentor: [
      { id: 'm3', senderId: 'mentor', text: 'Hello Alex, let me know if you need guidance for the CS302 project submission.', time: 'Yesterday', isMe: false, read: true },
      { id: 'm4', senderId: 'me', text: 'Thank you Dr. Vance, the dataset pipeline is completed.', time: 'Yesterday', isMe: true, read: true },
    ]
  });

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMsg.trim()) return;

    const newMsg: Message = {
      id: Date.now().toString(),
      senderId: 'me',
      text: inputMsg,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isMe: true,
      read: true
    };

    setMessages((prev) => ({
      ...prev,
      [activeContact.id]: [...(prev[activeContact.id] || []), newMsg]
    }));

    setInputMsg('');
    showToast(`Message sent to ${activeContact.name}`, 'success');
  };

  return (
    <div className="glass-card rounded-2xl border border-slate-800 h-[600px] flex flex-col md:flex-row overflow-hidden shadow-2xl">
      {/* Contact List Sidebar */}
      <div className="w-full md:w-64 border-r border-slate-800 bg-slate-950/60 p-4 space-y-3">
        <div className="text-xs font-bold text-slate-400 uppercase font-mono tracking-wider mb-2 flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-brand-400" />
          Conversations
        </div>

        {contacts.map((c) => (
          <button
            key={c.id}
            onClick={() => setActiveContact(c)}
            className={`w-full text-left p-3 rounded-xl transition flex items-center gap-3 border ${
              activeContact.id === c.id
                ? 'bg-brand-600/15 border-brand-500/30 text-slate-100 shadow-md'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
            }`}
          >
            <div className="w-9 h-9 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-brand-400">
              {c.avatar}
            </div>
            <div>
              <div className="text-xs font-bold">{c.name}</div>
              <div className="text-[10px] text-slate-500">{c.role}</div>
            </div>
          </button>
        ))}
      </div>

      {/* Main Chat Conversation */}
      <div className="flex-1 flex flex-col justify-between bg-slate-900/40">
        {/* Chat Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/40">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center font-bold text-brand-400 text-xs">
              {activeContact.avatar}
            </div>
            <div>
              <div className="text-xs font-bold text-slate-100">{activeContact.name}</div>
              <div className="text-[10px] text-emerald-400 font-mono">🟢 Online • StudIQ Encrypted Channel</div>
            </div>
          </div>
        </div>

        {/* Message History Container */}
        <div className="p-4 overflow-y-auto space-y-3 flex-1">
          {(messages[activeContact.id] || []).map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col ${msg.isMe ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-md p-3 rounded-2xl text-xs leading-relaxed ${
                  msg.isMe
                    ? 'bg-brand-600 text-white rounded-br-none shadow-md'
                    : 'bg-slate-800 text-slate-200 rounded-bl-none border border-slate-700/80'
                }`}
              >
                {msg.text}
              </div>
              <span className="text-[10px] text-slate-500 mt-1 font-mono flex items-center gap-1">
                {msg.time} {msg.isMe && <CheckCheck className="w-3 h-3 text-brand-400" />}
              </span>
            </div>
          ))}
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSendMessage} className="p-3 border-t border-slate-800 bg-slate-950/60 flex items-center gap-2">
          <input
            type="text"
            value={inputMsg}
            onChange={(e) => setInputMsg(e.target.value)}
            placeholder={`Message ${activeContact.name}...`}
            className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition"
          />
          <button
            type="submit"
            className="bg-brand-600 hover:bg-brand-500 text-white p-2.5 rounded-xl shadow-lg shadow-brand-500/20 transition"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
