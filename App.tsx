
import React, { useState, useEffect, useRef } from 'react';
import PacketBuilder from './components/PacketBuilder';
import PacketParser from './components/PacketParser';
import GeminiAssistant from './components/GeminiAssistant';
import ScriptGenerator from './components/ScriptGenerator';
import { LogEntry, CommandCode } from './types';
import { simulateResponse, hexToBytes, unescapeData, buildPacket } from './utils/protocolUtils';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'tools' | 'assistant' | 'realworld'>('tools');
  const [parserInput, setParserInput] = useState<string>('FE 03 00 21 02 24 FF');
  const [currentBuilderHex, setCurrentBuilderHex] = useState<string>('FE 03 00 21 02 24 FF');
  const [activityLog, setActivityLog] = useState<LogEntry[]>([]);
  const consoleRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (consoleRef.current) {
      consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
    }
  }, [activityLog]);

  const addLog = (direction: 'TX' | 'RX', hex: string) => {
    const bytes = hexToBytes(hex);
    const { unescaped } = unescapeData(bytes.slice(2, bytes.length - 2));
    const cmd = unescaped[1];
    const cmdName = CommandCode[cmd] || 'Unknown';
    
    const newEntry: LogEntry = {
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
      direction,
      hex,
      summary: cmdName
    };
    setActivityLog(prev => [...prev, newEntry]);
  };

  const handleSendPacket = (hex: string) => {
    setCurrentBuilderHex(hex);
    addLog('TX', hex);
    setTimeout(() => {
      const responseHex = simulateResponse(hex);
      if (responseHex) addLog('RX', responseHex);
    }, 800);
  };

  return (
    <div className="min-h-screen pb-12 bg-slate-50">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-indigo-600 p-2 rounded-lg">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h1 className="font-black text-xl tracking-tight text-slate-800 uppercase">RackLink<span className="text-indigo-600 text-sm font-normal align-top ml-0.5">™</span></h1>
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-none">Protocol Explorer v1.2</p>
            </div>
          </div>
          
          <nav className="flex gap-1 bg-slate-100 p-1 rounded-lg">
            <button 
              onClick={() => setActiveTab('tools')}
              className={`px-4 py-1.5 rounded-md text-sm font-bold transition-all ${
                activeTab === 'tools' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              Tools
            </button>
            <button 
              onClick={() => setActiveTab('realworld')}
              className={`px-4 py-1.5 rounded-md text-sm font-bold transition-all ${
                activeTab === 'realworld' ? 'bg-white text-orange-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              Deployment
            </button>
            <button 
              onClick={() => setActiveTab('assistant')}
              className={`px-4 py-1.5 rounded-md text-sm font-bold transition-all ${
                activeTab === 'assistant' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              AI Consultant
            </button>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 pt-8">
        {activeTab === 'tools' && (
          <div className="space-y-8 animate-in fade-in duration-500">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
              <div className="space-y-8">
                <PacketBuilder onSend={handleSendPacket} />
                <div className="bg-indigo-900 rounded-xl p-6 text-white overflow-hidden relative shadow-lg">
                  <h3 className="text-lg font-bold mb-3 flex items-center gap-2">
                    <span className="text-indigo-400">⚡</span>
                    Protocol Quick Ref
                  </h3>
                  <div className="grid grid-cols-2 gap-4 text-xs opacity-90">
                    <div className="space-y-2">
                      <div className="flex justify-between"><span>Header:</span><code className="bg-indigo-800 px-1 rounded">0xFE</code></div>
                      <div className="flex justify-between"><span>Tail:</span><code className="bg-indigo-800 px-1 rounded">0xFF</code></div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between"><span>Escape:</span><code className="bg-indigo-800 px-1 rounded">0xFD</code></div>
                      <div className="flex justify-between"><span>Checksum:</span><code className="bg-indigo-800 px-1 rounded">7-bit</code></div>
                    </div>
                  </div>
                </div>
              </div>
              <PacketParser input={parserInput} setInput={setParserInput} />
            </div>

            <div className="bg-slate-900 rounded-2xl border border-slate-800 shadow-2xl overflow-hidden">
              <div className="bg-slate-800/50 px-6 py-3 border-b border-slate-700 flex justify-between items-center">
                <h3 className="text-slate-300 font-bold text-sm uppercase tracking-wider flex items-center gap-2">
                  <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                  Communication Console
                </h3>
                <button onClick={() => setActivityLog([])} className="text-slate-500 hover:text-slate-300 text-xs font-bold uppercase">Clear Log</button>
              </div>
              <div ref={consoleRef} className="h-[300px] overflow-y-auto p-4 font-mono text-sm space-y-2 scrollbar-thin scrollbar-thumb-slate-700">
                {activityLog.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-slate-600 space-y-2 text-center">
                    <p className="italic">Awaiting data transmission... Try sending a packet above.</p>
                  </div>
                ) : (
                  activityLog.map((log) => (
                    <div 
                      key={log.id} 
                      className="group flex gap-4 p-2 rounded hover:bg-slate-800/50 cursor-pointer transition-colors"
                      onClick={() => setParserInput(log.hex)}
                    >
                      <span className="text-slate-500 w-20 shrink-0">{log.timestamp.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
                      <span className={`w-8 font-black shrink-0 ${log.direction === 'TX' ? 'text-indigo-400' : 'text-emerald-400'}`}>{log.direction}</span>
                      <span className="text-slate-200 break-all flex-1">{log.hex}</span>
                      <span className="text-slate-500 italic shrink-0 group-hover:text-slate-300">{log.summary}</span>
                      <span className="opacity-0 group-hover:opacity-100 text-indigo-400 text-[10px] uppercase font-bold self-center">Inspect →</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'realworld' && (
          <div className="max-w-5xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="mb-8">
              <h2 className="text-3xl font-black text-slate-800 mb-2">Deploy to RLNK-SW715R</h2>
              <p className="text-slate-500">Generate code snippets to communicate with your physical Middle Atlantic hardware using the selected packet.</p>
            </div>
            <ScriptGenerator hex={currentBuilderHex} />
          </div>
        )}

        {activeTab === 'assistant' && (
          <div className="max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
            <GeminiAssistant />
          </div>
        )}
      </main>

      <footer className="max-w-7xl mx-auto px-4 mt-12 pt-8 border-t border-slate-200 flex flex-col md:flex-row justify-between items-center gap-4 text-slate-400 text-[10px] font-bold uppercase tracking-widest">
        <p>© 2024 Middle Atlantic. Simulation and Protocol Reference Tool.</p>
        <div className="flex gap-6">
          <span>Monitor</span>
          <span>Control</span>
          <span>Analyze</span>
        </div>
      </footer>
    </div>
  );
};

export default App;
