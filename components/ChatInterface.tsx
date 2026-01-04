
import React, { useState, useRef, useEffect } from 'react';
import { getGeminiResponse, getTTSAudio, decodeBase64, decodeAudioData } from '../services/geminiService';
import { ChatMode, Message } from '../types';

interface ChatInterfaceProps {
  playerName: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ playerName }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { 
      role: 'assistant', 
      content: `Hello ${playerName}, I've synchronized your career history. I'm here to help optimize your path. What can I analyze for you?`, 
      timestamp: new Date() 
    }
  ]);
  const [input, setInput] = useState('');
  const [mode, setMode] = useState<ChatMode>(ChatMode.FAST);
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isOpen]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: input, mode, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const prompt = `Act as COI (Career Optimization Interface), a high-level elite professional athlete agent.
                     Active Player Profile: ${playerName}.
                     
                     User Query: ${input}.
                     
                     Provide highly accurate simulated data-driven insights based on real NBA history and projections. 
                     Keep responses concise but expert.`;
      
      const response = await getGeminiResponse(prompt, mode === ChatMode.THINK ? 'think' : 'fast');
      
      const aiMessage: Message = { 
        role: 'assistant', 
        content: response || "I'm having connectivity issues with the data core.", 
        mode, 
        timestamp: new Date() 
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTTS = async (text: string) => {
    try {
      const base64Audio = await getTTSAudio(text);
      if (base64Audio) {
        if (!audioContextRef.current) {
          audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });
        }
        const ctx = audioContextRef.current;
        if (ctx.state === 'suspended') await ctx.resume();
        const audioBuffer = await decodeAudioData(decodeBase64(base64Audio), ctx);
        const source = ctx.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(ctx.destination);
        source.start();
      }
    } catch (error) {
      console.error("TTS failed", error);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end pointer-events-none">
      {/* Chat Window */}
      {isOpen && (
        <div className="w-[380px] h-[520px] bg-[#121214] border border-white/10 rounded-3xl overflow-hidden shadow-2xl flex flex-col mb-4 pointer-events-auto animate-in slide-in-from-bottom-4 duration-300">
          <div className="p-4 bg-zinc-900 border-b border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-[10px] font-black shadow-lg shadow-blue-500/20">COI</div>
              <div>
                <span className="text-xs font-bold block leading-none">Intelligence Studio</span>
                <span className="text-[9px] text-green-500 font-mono uppercase tracking-tighter">Active Agent</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
               <div className="flex bg-zinc-800 p-0.5 rounded-lg border border-white/5">
                 <button onClick={() => setMode(ChatMode.FAST)} className={`px-2 py-1 text-[8px] font-bold uppercase rounded-md transition-all ${mode === ChatMode.FAST ? 'bg-blue-600 text-white' : 'text-zinc-500'}`}>Fast</button>
                 <button onClick={() => setMode(ChatMode.THINK)} className={`px-2 py-1 text-[8px] font-bold uppercase rounded-md transition-all ${mode === ChatMode.THINK ? 'bg-purple-600 text-white' : 'text-zinc-500'}`}>Think</button>
               </div>
               <button onClick={() => setIsOpen(false)} className="text-zinc-500 hover:text-white p-1">
                 <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
               </button>
            </div>
          </div>

          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-2xl p-3 ${
                  msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-tr-none' 
                  : 'bg-zinc-800 text-zinc-200 rounded-tl-none border border-white/5'
                }`}>
                  <p className="text-[11px] leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                  <div className="flex justify-between items-center mt-2 opacity-40">
                     <span className="text-[8px] uppercase font-bold">{msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                     {msg.role === 'assistant' && (
                       <button onClick={() => handleTTS(msg.content)} className="hover:text-blue-400">
                         <span className="text-[10px]">🔊</span>
                       </button>
                     )}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-zinc-800/50 p-3 rounded-2xl rounded-tl-none border border-white/5 flex gap-1.5 items-center">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"></div>
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                </div>
              </div>
            )}
          </div>

          <div className="p-3 bg-zinc-900 border-t border-white/5">
            <div className="flex gap-2 bg-zinc-800/50 p-1.5 rounded-xl border border-white/5 shadow-inner">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Ask your agent..."
                className="flex-1 bg-transparent px-3 py-1.5 text-xs focus:outline-none placeholder:text-zinc-600 font-medium"
              />
              <button
                onClick={handleSend}
                disabled={isLoading}
                className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 p-1.5 rounded-lg transition-all text-white shadow-lg shadow-blue-500/20"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Floating Toggle Bubble */}
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="pointer-events-auto w-14 h-14 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-full flex items-center justify-center shadow-xl shadow-blue-500/40 hover:scale-110 active:scale-95 transition-all group relative"
      >
        <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-10 transition-opacity rounded-full"></div>
        {isOpen ? (
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" /></svg>
        ) : (
          <div className="relative">
             <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg>
             <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 border-2 border-white rounded-full animate-pulse"></div>
          </div>
        )}
      </button>
    </div>
  );
};

export default ChatInterface;
