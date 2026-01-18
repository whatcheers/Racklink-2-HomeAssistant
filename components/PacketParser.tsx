
import React, { useMemo } from 'react';
import { parsePacket } from '../utils/protocolUtils';

interface PacketParserProps {
  input: string;
  setInput: (val: string) => void;
}

const PacketParser: React.FC<PacketParserProps> = ({ input, setInput }) => {
  const breakdown = useMemo(() => parsePacket(input), [input]);

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-full">
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        <span className="p-2 bg-emerald-100 text-emerald-600 rounded-lg">🔍</span>
        Protocol Parser
      </h2>

      <div className="mb-6">
        <label className="block text-sm font-medium text-slate-700 mb-1">Paste Hex String</label>
        <textarea 
          className="w-full p-3 border border-slate-300 rounded-md focus:ring-2 focus:ring-emerald-500 outline-none font-mono h-24 transition-all"
          placeholder="FE 04 00 20 02 01 25 FF"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
      </div>

      <div className="space-y-3 overflow-y-auto max-h-[400px] pr-2 scrollbar-thin scrollbar-thumb-slate-200">
        {breakdown.length > 0 ? (
          breakdown.map((item, idx) => (
            <div key={idx} className="flex flex-col md:flex-row md:items-start gap-2 border-l-4 border-emerald-500 pl-4 py-1 hover:bg-emerald-50/50 transition-colors">
              <div className="w-32 shrink-0">
                <span className="font-bold text-[10px] text-slate-400 uppercase tracking-tighter block leading-none mb-1">{item.label}</span>
                <code className="bg-emerald-100 px-1.5 py-0.5 rounded text-emerald-700 font-mono font-bold text-sm">{item.hex}</code>
              </div>
              <span className="text-slate-600 text-sm md:mt-4 flex-1">— {item.description}</span>
            </div>
          ))
        ) : (
          <div className="text-center py-12 text-slate-400 italic bg-slate-50 rounded-lg border-2 border-dashed border-slate-200">
            Enter a hex string starting with FE and ending with FF to begin inspection
          </div>
        )}
      </div>
    </div>
  );
};

export default PacketParser;
