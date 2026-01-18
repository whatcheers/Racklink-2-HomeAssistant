
import React, { useState, useRef, useEffect } from 'react';
import { GoogleGenAI } from "@google/genai";

const GeminiAssistant: React.FC = () => {
  const [messages, setMessages] = useState<{role: 'user' | 'assistant', text: string}[]>([
    { role: 'assistant', text: "Hello! I'm the RackLink Protocol Assistant. How can I help you with the communication protocol today?" }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setInput('');
    setIsLoading(true);

    try {
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      const response = await ai.models.generateContent({
        model: "gemini-3-flash-preview",
        contents: userMsg,
        config: {
          systemInstruction: `You are an expert on the Middle Atlantic RackLink™ Control System Communication Protocol. 
          Use the following rules to help the user:
          - Packets start with 0xFE and end with 0xFF.
          - Byte 2 is the length of the data envelope.
          - The Checksum is the 7-bit sum of all bytes from Header to end of Data Envelope (sum & 0x7F).
          - Protected values (0xFE, 0xFF, 0xFD) must be escaped by 0xFD followed by bit-inverted value.
          - Common Commands: Login (0x02), Power (0x20), EPO (0x37), Sensors (0x50-0x61).
          Help debug hex strings, explain command structures, or provide code examples.`,
        },
      });

      const aiText = response.text || "I'm sorry, I couldn't generate a response.";
      setMessages(prev => [...prev, { role: 'assistant', text: aiText }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', text: "Error connecting to AI assistant. Please check your connection." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-slate-900 text-white p-6 rounded-xl shadow-xl flex flex-col h-[500px]">
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        <span className="p-2 bg-slate-800 text-indigo-400 rounded-lg">🤖</span>
        Protocol Assistant
      </h2>
      
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto mb-4 space-y-4 pr-2 scrollbar-thin scrollbar-thumb-slate-700"
      >
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] p-3 rounded-lg text-sm ${
              m.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-200'
            }`}>
              {m.text}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-800 p-3 rounded-lg text-xs italic text-slate-400 animate-pulse">
              Assistant is thinking...
            </div>
          </div>
        )}
      </div>

      <div className="flex gap-2">
        <input 
          type="text"
          className="flex-1 bg-slate-800 border-none rounded-md px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none text-sm"
          placeholder="Ask about a command..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <button 
          onClick={handleSend}
          disabled={isLoading}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 px-4 py-2 rounded-md transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default GeminiAssistant;
