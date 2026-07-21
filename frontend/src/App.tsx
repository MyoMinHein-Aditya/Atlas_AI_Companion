import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, Terminal, CheckCircle2, Loader2, Wifi, WifiOff, 
  Command, X, Square, Minus, Plus, MessageSquare, Menu, ShieldAlert,
  Settings, Sun, Moon, Volume2, VolumeX, Sliders
} from 'lucide-react';

interface Message {
  sender: 'user' | 'atlas';
  content: string;
}

interface SessionItem {
  id: string;
  title: string;
  summary: string | null;
  updated_at: string;
}

interface ExecutionLog {
  step: number;
  status: 'RUNNING' | 'SUCCESS' | 'ERROR';
  description: string;
}

/* Sub-Component: Settings Modal */
function SettingsModal({ 
  open, 
  onClose, 
  isLight, 
  themeMode, 
  setThemeMode, 
  voiceEnabled, 
  setVoiceEnabled, 
  voiceVolume, 
  setVoiceVolume, 
  autoApprove, 
  setAutoApprove 
}: any) {
  if (!open) return null;
  return (
    <div className="absolute inset-0 bg-black/70 flex items-center justify-center p-6 z-50">
      <motion.div 
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className={`max-w-md w-full border rounded-xl p-6 shadow-2xl flex flex-col gap-6 ${
          isLight ? 'bg-white border-zinc-300 text-zinc-900' : 'bg-zinc-900 border-zinc-800 text-zinc-100'
        }`}
      >
        <div className="flex items-center justify-between border-b pb-3 border-zinc-800">
          <div className="flex items-center gap-2 font-mono text-xs font-bold tracking-wider">
            <Sliders className="h-4 w-4" />
            SYSTEM CONFIGURATION SETTINGS
          </div>
          <button onClick={onClose} className="p-1 hover:bg-zinc-800 rounded">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between items-center text-xs font-mono">
            <span className="flex items-center gap-1.5">
              {isLight ? <Sun className="h-3.5 w-3.5" /> : <Moon className="h-3.5 w-3.5" />}
              THEME MODE
            </span>
            <span className="uppercase text-[10px] text-zinc-400 font-bold">{themeMode} MODE</span>
          </div>
          <button
            onClick={() => setThemeMode(isLight ? 'dark' : 'light')}
            className={`w-full py-2.5 px-4 rounded-lg border flex items-center justify-between font-mono text-xs transition-colors ${
              isLight ? 'bg-zinc-100 border-zinc-300 text-zinc-900 hover:bg-zinc-200' : 'bg-zinc-950 border-zinc-800 text-zinc-100 hover:bg-zinc-800'
            }`}
          >
            <span className="flex items-center gap-2">
              {isLight ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              <span>TOGGLE TO {isLight ? 'DARK' : 'LIGHT'} MODE</span>
            </span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-zinc-800 text-zinc-200">
              {isLight ? 'LIGHT' : 'DARK'}
            </span>
          </button>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between items-center text-xs font-mono">
            <span className="flex items-center gap-1.5">
              {voiceEnabled ? <Volume2 className="h-3.5 w-3.5" /> : <VolumeX className="h-3.5 w-3.5" />}
              VOICE OUTPUT MODE
            </span>
            <span className="text-[10px] text-zinc-400 font-bold">{voiceEnabled ? `${voiceVolume}%` : 'MUTED'}</span>
          </div>
          <div className="flex items-center gap-3">
            <button 
              onClick={() => setVoiceEnabled(!voiceEnabled)}
              className={`px-2 py-1 rounded text-[10px] font-mono border ${voiceEnabled ? 'bg-zinc-800 text-zinc-100 border-zinc-600' : 'bg-transparent text-zinc-500 border-zinc-800'}`}
            >
              {voiceEnabled ? 'ENABLED' : 'DISABLED'}
            </button>
            <input 
              type="range" 
              min="0" 
              max="100" 
              value={voiceEnabled ? voiceVolume : 0}
              disabled={!voiceEnabled}
              onChange={(e) => setVoiceVolume(Number(e.target.value))}
              className="w-full h-1.5 bg-zinc-700 rounded-lg appearance-none cursor-pointer accent-zinc-200 disabled:opacity-30"
            />
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between items-center text-xs font-mono">
            <span>AUTO-APPROVE COMMANDS</span>
            <span className="text-[10px] text-zinc-400 font-bold">{autoApprove ? 'ON' : 'OFF'}</span>
          </div>
          <div className="flex items-center justify-between p-2.5 rounded border border-zinc-800 bg-zinc-950 text-xs font-mono">
            <span className="text-[11px] text-zinc-400">Execute safe app launches & commands without pop-up prompts</span>
            <input 
              type="checkbox" 
              checked={autoApprove}
              onChange={(e) => setAutoApprove(e.target.checked)}
              className="h-4 w-4 cursor-pointer accent-zinc-200"
            />
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button onClick={onClose} className={`px-4 py-2 rounded-lg text-xs font-mono font-semibold ${isLight ? 'bg-zinc-900 text-white' : 'bg-zinc-100 text-zinc-950'}`}>
            SAVE & CLOSE
          </button>
        </div>
      </motion.div>
    </div>
  );
}

/* Sub-Component: Chat Message Item */
function ChatMessageItem({ msg, isLight, isGenerating }: { msg: Message; isLight: boolean; isGenerating: boolean }) {
  return (
    <motion.div
      initial={{ y: 10, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.15, ease: 'easeOut' }}
      className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
    >
      <div 
        className={`max-w-[75%] px-4 py-3 rounded-xl border text-sm leading-relaxed ${
          msg.sender === 'user'
            ? isLight ? 'bg-zinc-900 border-zinc-900 text-white rounded-br-none' : 'bg-zinc-900 border-zinc-700 text-zinc-100 rounded-br-none'
            : isLight ? 'bg-white border-zinc-300 text-zinc-900 rounded-bl-none shadow-sm' : 'bg-zinc-900/40 border-zinc-800 text-zinc-200 rounded-bl-none'
        }`}
      >
        {msg.content === '' && isGenerating ? (
          <div className="flex items-center gap-2 py-1 text-zinc-400">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-xs font-mono">Formulating...</span>
          </div>
        ) : (
          msg.content
        )}
      </div>
    </motion.div>
  );
}

function App() {
  const [prompt, setPrompt] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    { sender: 'atlas', content: 'Greeting client. I am Atlas, your desktop operating companion. How can I assist you today?' }
  ]);
  const [logs, setLogs] = useState<ExecutionLog[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const [settingsOpen, setSettingsOpen] = useState(false);
  const [themeMode, setThemeMode] = useState<'dark' | 'light'>('dark');
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [voiceVolume, setVoiceVolume] = useState(80);
  const [autoApprove, setAutoApprove] = useState(true);

  const [pendingApproval, setPendingApproval] = useState<{ command: string; step: number } | null>(null);

  const socketRef = useRef<WebSocket | null>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const connectWebSocket = () => {
    const ws = new WebSocket('ws://localhost:8000/ws/stream');
    ws.onopen = () => setIsConnected(true);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'chat_token') {
          setMessages((prev) => {
            const last = prev[prev.length - 1];
            return (last && last.sender === 'atlas')
              ? [...prev.slice(0, -1), { sender: 'atlas', content: last.content + data.token }]
              : [...prev, { sender: 'atlas', content: data.token }];
          });
        } else if (data.type === 'session_created') {
          setActiveSessionId(data.session_id);
          fetchSessions();
        } else if (data.type === 'approval_required') {
          autoApprove ? handleApproval(true) : setPendingApproval({ command: data.command, step: data.step });
        } else if (data.type === 'execution_status') {
          setIsGenerating(true);
          setLogs((prev) => {
            const index = prev.findIndex((l) => l.step === data.step);
            if (index !== -1) {
              const updated = [...prev];
              updated[index] = { step: data.step, status: data.status, description: data.description };
              return updated;
            }
            return [...prev, { step: data.step, status: data.status, description: data.description }];
          });
          if (data.status === 'SUCCESS' || data.status === 'ERROR') {
            setIsGenerating(false);
            fetchSessions();
          }
        }
      } catch (err) {
        console.error('WebSocket parse error:', err);
      }
    };
    ws.onclose = () => {
      setIsConnected(false);
      setIsGenerating(false);
      setTimeout(connectWebSocket, 3000);
    };
    socketRef.current = ws;
  };

  const fetchSessions = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/sessions');
      if (res.ok) setSessions(await res.json());
    } catch (err) {
      console.error('Fetch sessions failed:', err);
    }
  };

  const loadSession = async (sessionId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/sessions/${sessionId}/messages`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data.length > 0 ? data : [{ sender: 'atlas', content: 'Empty session.' }]);
        setActiveSessionId(sessionId);
        setLogs([]);
      }
    } catch (err) {
      console.error('Load session failed:', err);
    }
  };

  const startNewSession = () => {
    setActiveSessionId(null);
    setMessages([{ sender: 'atlas', content: 'New session started. How can I assist you today?' }]);
    setLogs([]);
    inputRef.current?.focus();
  };

  useEffect(() => {
    connectWebSocket();
    fetchSessions();
    const unsubscribe = window.electron?.onSummon?.(() => inputRef.current?.focus());
    return () => {
      unsubscribe?.();
      socketRef.current?.close();
    };
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, logs]);

  const handleSend = () => {
    if (!prompt.trim()) return;
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      setMessages((prev) => [...prev, { sender: 'user', content: prompt }]);
      socketRef.current.send(JSON.stringify({
        type: 'text_prompt',
        content: prompt,
        session_id: activeSessionId,
        history: messages.map(m => ({ sender: m.sender, content: m.content }))
      }));
      setMessages((prev) => [...prev, { sender: 'atlas', content: '' }]);
      setLogs([]);
      setPrompt('');
      setIsGenerating(true);
    }
  };

  const handleApproval = (approved: boolean) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: 'approval_response', approved }));
    }
    setPendingApproval(null);
  };

  const isLight = themeMode === 'light';

  return (
    <div className={`flex h-screen w-screen select-none overflow-hidden border rounded-xl relative transition-colors duration-200 ${
      isLight ? 'bg-zinc-50 border-zinc-300 text-zinc-900' : 'bg-zinc-950 border-zinc-800 text-zinc-100'
    }`}>
      
      <SettingsModal 
        open={settingsOpen} 
        onClose={() => setSettingsOpen(false)} 
        isLight={isLight}
        themeMode={themeMode}
        setThemeMode={setThemeMode}
        voiceEnabled={voiceEnabled}
        setVoiceEnabled={setVoiceEnabled}
        voiceVolume={voiceVolume}
        setVoiceVolume={setVoiceVolume}
        autoApprove={autoApprove}
        setAutoApprove={setAutoApprove}
      />

      {/* Security Approval Overlay */}
      <AnimatePresence>
        {pendingApproval && !autoApprove && (
          <div className="absolute inset-0 bg-black/80 flex items-center justify-center p-6 z-50">
            <motion.div initial={{ scale: 0.98, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.98, opacity: 0 }} className={`max-w-md w-full border rounded-xl p-6 shadow-2xl flex flex-col gap-4 ${isLight ? 'bg-white border-zinc-300 text-zinc-900' : 'bg-zinc-900 border-zinc-800 text-zinc-100'}`}>
              <div className="flex items-center gap-2 font-mono text-xs font-bold">
                <ShieldAlert className="h-4 w-4 text-zinc-400" />
                SECURITY AUTHORIZATION REQUEST
              </div>
              <div className="text-xs text-zinc-400">Atlas is requesting permission to execute:</div>
              <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-3 font-mono text-xs text-zinc-200 select-text overflow-x-auto break-all max-h-36 custom-scrollbar">
                $ {pendingApproval.command}
              </div>
              <div className="flex justify-end gap-3 mt-2">
                <button onClick={() => handleApproval(false)} className="px-4 py-2 rounded-lg border border-zinc-700 text-xs font-mono text-zinc-400">DENY</button>
                <button onClick={() => handleApproval(true)} className={`px-4 py-2 rounded-lg text-xs font-mono font-semibold ${isLight ? 'bg-zinc-900 text-white' : 'bg-zinc-100 text-zinc-950'}`}>APPROVE</button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <AnimatePresence initial={false}>
        {sidebarOpen && (
          <motion.div initial={{ width: 0, opacity: 0 }} animate={{ width: 240, opacity: 1 }} exit={{ width: 0, opacity: 0 }} transition={{ duration: 0.2 }} className={`h-full border-r flex flex-col z-20 overflow-hidden ${isLight ? 'bg-zinc-100 border-zinc-300' : 'bg-zinc-950 border-zinc-800'}`}>
            <div className={`p-4 border-b flex items-center justify-between ${isLight ? 'border-zinc-300' : 'border-zinc-800'}`}>
              <span className="text-[10px] tracking-[0.2em] font-bold font-mono text-zinc-400">HISTORY</span>
              <button onClick={startNewSession} className={`p-1 border rounded ${isLight ? 'hover:bg-zinc-200 border-zinc-300 text-zinc-700' : 'hover:bg-zinc-800 border-zinc-800 text-zinc-400'}`}>
                <Plus className="h-3.5 w-3.5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-2 space-y-1 custom-scrollbar">
              {sessions.map((s) => (
                <button key={s.id} onClick={() => loadSession(s.id)} className={`w-full text-left px-3 py-2.5 rounded-lg flex items-center gap-2.5 border transition-all text-xs ${s.id === activeSessionId ? (isLight ? 'bg-zinc-200 border-zinc-400 text-zinc-900' : 'bg-zinc-900 border-zinc-700 text-zinc-100') : (isLight ? 'text-zinc-600 hover:bg-zinc-200/60' : 'text-zinc-400 hover:bg-zinc-900/60')}`}>
                  <MessageSquare className="h-3.5 w-3.5 shrink-0" />
                  <span className="truncate">{s.title || 'Untitled Session'}</span>
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Panel */}
      <div className={`flex-1 flex flex-col h-full relative overflow-hidden ${isLight ? 'bg-zinc-50' : 'bg-zinc-950'}`}>
        
        {/* Title Bar */}
        <div className={`flex items-center justify-between px-4 py-3 border-b drag-region select-none z-10 ${isLight ? 'bg-zinc-100 border-zinc-300' : 'bg-zinc-950 border-zinc-800'}`}>
          <div className="flex items-center gap-3">
            <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-1 text-zinc-400 hover:text-zinc-200"><Menu className="h-4 w-4" /></button>
            <div className="flex items-center gap-2">
              <div className={`h-2 w-2 rounded-full ${isLight ? 'bg-zinc-900' : 'bg-zinc-100'}`} />
              <span className={`font-bold tracking-[0.2em] text-xs font-mono ${isLight ? 'text-zinc-900' : 'text-zinc-100'}`}>ATLAS</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => setSettingsOpen(true)} className="p-1 border rounded text-xs font-mono flex items-center gap-1 border-zinc-800"><Settings className="h-3.5 w-3.5" /></button>
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded border text-[10px] font-mono border-zinc-800">
              {isConnected ? <Wifi className="h-3 w-3 text-emerald-500" /> : <WifiOff className="h-3 w-3 text-rose-500" />}
              <span>{isConnected ? 'ONLINE' : 'OFFLINE'}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <button onClick={() => window.electron?.minimize?.()} className="p-1 text-zinc-400"><Minus className="h-3.5 w-3.5" /></button>
              <button onClick={() => window.electron?.maximize?.()} className="p-1 text-zinc-400"><Square className="h-3 w-3" /></button>
              <button onClick={() => window.electron?.close?.()} className="p-1 text-zinc-400"><X className="h-3.5 w-3.5" /></button>
            </div>
          </div>
        </div>

        {/* Chat List */}
        <div className="flex-1 flex flex-col overflow-y-auto px-6 py-4 custom-scrollbar space-y-4 z-10">
          <div className="flex-1 space-y-4">
            {messages.map((m, idx) => (
              <ChatMessageItem key={idx} msg={m} isLight={isLight} isGenerating={isGenerating} />
            ))}
            <div ref={chatEndRef} />
          </div>

          {/* Execution Pipeline Logs */}
          <AnimatePresence>
            {logs.length > 0 && (
              <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className={`border rounded-xl overflow-hidden ${isLight ? 'border-zinc-300 bg-white' : 'border-zinc-800 bg-zinc-900'}`}>
                <div className="flex items-center gap-2 px-3 py-2 border-b text-xs font-mono font-bold border-zinc-800 text-zinc-400"><Terminal className="h-3.5 w-3.5" />EXECUTION PIPELINE</div>
                <div className="p-3 space-y-2 text-xs font-mono select-text">
                  {logs.map((l) => (
                    <div key={l.step} className="flex items-start gap-2.5">
                      {l.status === 'RUNNING' ? <Loader2 className="h-3.5 w-3.5 animate-spin text-zinc-400 mt-0.5" /> : l.status === 'SUCCESS' ? <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 mt-0.5" /> : <X className="h-3.5 w-3.5 text-rose-500 mt-0.5" />}
                      <span className={l.status === 'RUNNING' ? 'text-zinc-800 font-semibold' : 'text-zinc-500'}>[Step {l.step}] <pre className="inline font-mono whitespace-pre-wrap">{l.description}</pre></span>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Input Bar */}
        <div className={`p-4 border-t z-10 flex flex-col gap-2 ${isLight ? 'bg-zinc-100 border-zinc-300' : 'bg-zinc-950 border-zinc-800'}`}>
          <div className="relative flex items-center">
            <div className="absolute left-3.5 flex items-center gap-1 font-mono text-[10px] px-1.5 py-0.5 border rounded border-zinc-800 text-zinc-500"><Command className="h-3 w-3" /><span>ALT + SPACE</span></div>
            <input ref={inputRef} type="text" placeholder="Instruct Atlas..." value={prompt} onChange={(e) => setPrompt(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleSend()} disabled={!isConnected} className={`w-full pl-36 pr-12 py-3.5 text-sm border rounded-xl placeholder-zinc-500 focus:outline-none transition-all ${isLight ? 'bg-white border-zinc-300 text-zinc-900' : 'bg-zinc-900 border-zinc-800 text-zinc-100'}`} />
            <div className="absolute right-3.5 flex items-center">
              <button onClick={handleSend} disabled={!prompt.trim() || !isConnected} className={`p-1.5 rounded-lg disabled:opacity-30 ${isLight ? 'bg-zinc-900 text-white' : 'bg-zinc-100 text-zinc-950'}`}><Send className="h-4 w-4" /></button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
