import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, Terminal, CheckCircle2, Loader2, Wifi, WifiOff, 
  Command, X, Square, Minus, Plus, MessageSquare, Menu, ShieldAlert 
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

function App() {
  const [prompt, setPrompt] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    { sender: 'atlas', content: 'Greeting client. I am Atlas, your desktop operating companion. How can I assist you today?' }
  ]);
  const [logs, setLogs] = useState<ExecutionLog[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  // Sessions and navigation states
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Security Approval state
  const [pendingApproval, setPendingApproval] = useState<{ command: string; step: number } | null>(null);

  const socketRef = useRef<WebSocket | null>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  // Connect to FastAPI local WebSocket server
  const connectWebSocket = () => {
    console.log('Connecting to WebSocket...');
    const ws = new WebSocket('ws://localhost:8000/ws/stream');

    ws.onopen = () => {
      console.log('WebSocket connected.');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('WebSocket message received:', data);

        if (data.type === 'chat_token') {
          setMessages((prev) => {
            const last = prev[prev.length - 1];
            if (last && last.sender === 'atlas') {
              return [
                ...prev.slice(0, -1),
                { sender: 'atlas', content: last.content + data.token }
              ];
            } else {
              return [...prev, { sender: 'atlas', content: data.token }];
            }
          });
        } else if (data.type === 'session_created') {
          setActiveSessionId(data.session_id);
          fetchSessions();
        } else if (data.type === 'approval_required') {
          setPendingApproval({
            command: data.command,
            step: data.step
          });
        } else if (data.type === 'execution_status') {
          setIsGenerating(true);
          setLogs((prev) => {
            const index = prev.findIndex((log) => log.step === data.step);
            if (index !== -1) {
              const updated = [...prev];
              updated[index] = {
                step: data.step,
                status: data.status,
                description: data.description
              };
              return updated;
            } else {
              return [
                ...prev,
                { step: data.step, status: data.status, description: data.description }
              ];
            }
          });
          if (data.status === 'SUCCESS' || data.status === 'ERROR') {
            setIsGenerating(false);
            fetchSessions();
          }
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket closed. Retrying in 3s...');
      setIsConnected(false);
      setIsGenerating(false);
      setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (err) => {
      console.error('WebSocket encountered an error:', err);
      ws.close();
    };

    socketRef.current = ws;
  };

  const fetchSessions = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/sessions');
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
      }
    } catch (err) {
      console.error('Failed to fetch sessions history:', err);
    }
  };

  const loadSession = async (sessionId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/sessions/${sessionId}/messages`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data.length > 0 ? data : [
          { sender: 'atlas', content: 'Empty session. Instruct Atlas to start logging.' }
        ]);
        setActiveSessionId(sessionId);
        setLogs([]);
      }
    } catch (err) {
      console.error('Failed to load session details:', err);
    }
  };

  const startNewSession = () => {
    setActiveSessionId(null);
    setMessages([
      { sender: 'atlas', content: 'New session started. How can I assist you today?' }
    ]);
    setLogs([]);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  useEffect(() => {
    connectWebSocket();
    fetchSessions();

    if (window.electron && window.electron.onSummon) {
      const unsubscribe = window.electron.onSummon(() => {
        if (inputRef.current) {
          inputRef.current.focus();
        }
      });
      return unsubscribe;
    }

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);

  // Auto-scroll chat window to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, logs]);

  const handleSend = () => {
    if (!prompt.trim()) return;

    const historyPayload = messages.map(m => ({ sender: m.sender, content: m.content }));

    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      setMessages((prev) => [...prev, { sender: 'user', content: prompt }]);
      
      socketRef.current.send(JSON.stringify({
        type: 'text_prompt',
        content: prompt,
        session_id: activeSessionId,
        history: historyPayload
      }));

      setMessages((prev) => [...prev, { sender: 'atlas', content: '' }]);
      setLogs([]);
      setPrompt('');
      setIsGenerating(true);
    } else {
      setMessages((prev) => [
        ...prev,
        { sender: 'user', content: prompt },
        { sender: 'atlas', content: 'Connection unavailable. Please verify that the backend server is running.' }
      ]);
      setPrompt('');
    }
  };

  // Dispatch User Approval Response over WebSockets
  const handleApproval = (approved: boolean) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        type: 'approval_response',
        approved: approved
      }));
    }
    setPendingApproval(null);
  };

  const handleMinimize = () => window.electron?.minimize?.();
  const handleMaximize = () => window.electron?.maximize?.();
  const handleClose = () => window.electron?.close?.();

  return (
    <div className="flex h-screen w-screen bg-zinc-950 text-zinc-100 select-none overflow-hidden border border-zinc-800 rounded-xl relative">
      
      {/* Security Consent Overlay Modal */}
      <AnimatePresence>
        {pendingApproval && (
          <div className="absolute inset-0 bg-black/80 flex items-center justify-center p-6 z-50">
            <motion.div 
              initial={{ scale: 0.98, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.98, opacity: 0 }}
              className="max-w-md w-full bg-zinc-900 border border-zinc-800 rounded-xl p-6 shadow-2xl flex flex-col gap-4"
            >
              <div className="flex items-center gap-2 text-zinc-200 font-mono text-xs font-bold">
                <ShieldAlert className="h-4 w-4 text-zinc-400" />
                SECURITY AUTHORIZATION REQUEST
              </div>
              
              <div className="text-xs text-zinc-400 leading-relaxed font-sans">
                Atlas is requesting permission to execute the following shell command on your computer. Please review carefully before approving:
              </div>
              
              <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-3 font-mono text-xs text-zinc-200 select-text overflow-x-auto break-all max-h-36 custom-scrollbar">
                $ {pendingApproval.command}
              </div>
              
              <div className="text-[10px] text-zinc-500 font-mono leading-relaxed">
                Failsafe Mechanism: Moving your cursor to any extreme corner of the screen immediately aborts active Python automation scripts.
              </div>
              
              <div className="flex items-center justify-end gap-3 mt-2">
                <button
                  onClick={() => handleApproval(false)}
                  className="px-4 py-2 rounded-lg border border-zinc-800 hover:bg-zinc-800 transition-colors text-xs font-mono text-zinc-400 hover:text-zinc-100"
                >
                  DENY
                </button>
                <button
                  onClick={() => handleApproval(true)}
                  className="px-4 py-2 rounded-lg bg-zinc-100 hover:bg-white text-zinc-950 transition-colors text-xs font-mono font-semibold"
                >
                  APPROVE
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Collapsible Left Conversations Sidebar */}
      <AnimatePresence initial={false}>
        {sidebarOpen && (
          <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 240, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            className="h-full border-r border-zinc-800 bg-zinc-950 flex flex-col z-20 overflow-hidden"
          >
            <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
              <span className="text-[10px] tracking-[0.2em] font-bold font-mono text-zinc-400">HISTORY</span>
              
              <button 
                onClick={startNewSession}
                className="p-1 hover:bg-zinc-800 border border-zinc-800 rounded text-zinc-400 hover:text-zinc-100 transition-colors"
                title="New Chat"
              >
                <Plus className="h-3.5 w-3.5" />
              </button>
            </div>

            {/* List of chat sessions */}
            <div className="flex-1 overflow-y-auto p-2 space-y-1 custom-scrollbar">
              {sessions.length === 0 ? (
                <div className="text-[10px] font-mono text-zinc-600 text-center py-6">
                  No sessions recorded
                </div>
              ) : (
                sessions.map((session) => {
                  const isActive = session.id === activeSessionId;
                  return (
                    <button
                      key={session.id}
                      onClick={() => loadSession(session.id)}
                      className={`w-full text-left px-3 py-2.5 rounded-lg flex items-center gap-2.5 border transition-all text-xs ${
                        isActive
                          ? 'bg-zinc-900 border-zinc-700 text-zinc-100'
                          : 'bg-transparent border-transparent text-zinc-400 hover:bg-zinc-900/60 hover:text-zinc-200'
                      }`}
                    >
                      <MessageSquare className={`h-3.5 w-3.5 shrink-0 ${isActive ? 'text-zinc-200' : 'text-zinc-500'}`} />
                      <span className="truncate pr-1 font-sans">{session.title || 'Untitled Session'}</span>
                    </button>
                  );
                })
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main chat window section */}
      <div className="flex-1 flex flex-col h-full relative overflow-hidden bg-zinc-950">

        {/* Custom Window Title Bar */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-950 drag-region select-none z-10">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1 hover:bg-zinc-800 rounded transition-colors text-zinc-400 hover:text-zinc-100"
              title="Toggle Sidebar"
            >
              <Menu className="h-4 w-4" />
            </button>

            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-zinc-100" />
              <span className="font-bold tracking-[0.2em] text-xs font-mono text-zinc-100">ATLAS</span>
              <span className="text-[10px] text-zinc-500 font-mono tracking-wider">v0.1.0</span>
            </div>
          </div>

          {/* Network Connection Indicator */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-[10px] font-mono">
              {isConnected ? (
                <>
                  <Wifi className="h-3 w-3 text-zinc-300" />
                  <span className="text-zinc-300">ONLINE</span>
                </>
              ) : (
                <>
                  <WifiOff className="h-3 w-3 text-zinc-500" />
                  <span className="text-zinc-500">OFFLINE</span>
                </>
              )}
            </div>

            {/* Window Control Buttons */}
            <div className="flex items-center gap-1.5">
              <button onClick={handleMinimize} className="p-1 hover:bg-zinc-800 rounded transition-colors text-zinc-400 hover:text-zinc-100">
                <Minus className="h-3.5 w-3.5" />
              </button>
              <button onClick={handleMaximize} className="p-1 hover:bg-zinc-800 rounded transition-colors text-zinc-400 hover:text-zinc-100">
                <Square className="h-3 w-3" />
              </button>
              <button onClick={handleClose} className="p-1 hover:bg-zinc-800 rounded transition-colors text-zinc-400 hover:text-zinc-100">
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col overflow-y-auto px-6 py-4 custom-scrollbar space-y-4 z-10">
          <div className="flex-1 space-y-4">
            {messages.map((msg, idx) => (
              <motion.div
                key={idx}
                initial={{ y: 10, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.2, ease: 'easeOut' }}
                className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div 
                  className={`max-w-[75%] px-4 py-3 rounded-xl border text-sm leading-relaxed ${
                    msg.sender === 'user'
                      ? 'bg-zinc-900 border-zinc-700 text-zinc-100 rounded-br-none'
                      : 'bg-zinc-900/40 border-zinc-800 text-zinc-200 rounded-bl-none'
                  }`}
                >
                  {msg.content === '' && isGenerating ? (
                    <div className="flex items-center gap-2 py-1 text-zinc-400">
                      <Loader2 className="h-4 w-4 animate-spin text-zinc-300" />
                      <span className="text-xs font-mono">Formulating...</span>
                    </div>
                  ) : (
                    msg.content
                  )}
                </div>
              </motion.div>
            ))}
            <div ref={chatEndRef} />
          </div>

          {/* Live Execution Logs Panel */}
          <AnimatePresence>
            {logs.length > 0 && (
              <motion.div 
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="border border-zinc-800 bg-zinc-900 rounded-xl overflow-hidden"
              >
                <div className="flex items-center gap-2 px-3 py-2 border-b border-zinc-800 bg-zinc-950 text-xs font-mono font-bold text-zinc-400">
                  <Terminal className="h-3.5 w-3.5 text-zinc-400" />
                  EXECUTION PIPELINE
                </div>
                <div className="p-3 space-y-2 text-xs font-mono select-text">
                  {logs.map((log) => (
                    <div key={log.step} className="flex items-start gap-2.5">
                      {log.status === 'RUNNING' ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin text-zinc-400 mt-0.5" />
                      ) : log.status === 'SUCCESS' ? (
                        <CheckCircle2 className="h-3.5 w-3.5 text-zinc-300 mt-0.5" />
                      ) : (
                        <X className="h-3.5 w-3.5 text-zinc-500 mt-0.5" />
                      )}
                      <span className={log.status === 'RUNNING' ? 'text-zinc-200' : 'text-zinc-400'}>
                        [Step {log.step}] <pre className="inline font-mono whitespace-pre-wrap">{log.description}</pre>
                      </span>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Input Command Area */}
        <div className="p-4 border-t border-zinc-800 bg-zinc-950 z-10 flex flex-col gap-2">
          <div className="relative flex items-center">
            <div className="absolute left-3.5 text-zinc-500 flex items-center gap-1 font-mono text-[10px] bg-zinc-900 px-1.5 py-0.5 border border-zinc-800 rounded">
              <Command className="h-3 w-3" />
              <span>ALT + SPACE</span>
            </div>

            <input
              ref={inputRef}
              type="text"
              placeholder="Instruct Atlas..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              disabled={!isConnected}
              className="w-full pl-36 pr-12 py-3.5 text-sm bg-zinc-900 border border-zinc-800 rounded-xl text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 transition-all font-sans"
            />

            <div className="absolute right-3.5 flex items-center">
              {/* Send Button */}
              <button
                onClick={handleSend}
                disabled={!prompt.trim() || !isConnected}
                className="p-1.5 rounded-lg bg-zinc-100 hover:bg-white text-zinc-950 disabled:opacity-30 transition-colors"
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between text-[10px] text-zinc-500 px-1 font-mono">
            <span>Powered by Gemini & Groq APIs</span>
            <span>Press Enter to dispatch script</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
