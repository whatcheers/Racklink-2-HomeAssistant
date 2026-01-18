
import React, { useState, useEffect } from 'react';
import { CommandCode, SubCommand } from '../types';
import { buildPacket, asciiToBytes } from '../utils/protocolUtils';

interface PacketBuilderProps {
  onSend: (hex: string) => void;
}

const PacketBuilder: React.FC<PacketBuilderProps> = ({ onSend }) => {
  const [command, setCommand] = useState<CommandCode>(CommandCode.OUTLET_NAME);
  const [subCommand, setSubCommand] = useState<SubCommand>(SubCommand.GET);
  const [params, setParams] = useState<string>('01');
  const [generatedHex, setGeneratedHex] = useState<string>('');
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    let dataEnvelope: number[] = [0x00, command, subCommand];
    
    if (command === CommandCode.LOGIN) {
      const loginStr = params || "user|password";
      dataEnvelope = [0x00, command, subCommand, ...asciiToBytes(loginStr)];
    } else if (params) {
      const cleanParams = params.replace(/[^0-9a-fA-F]/g, '');
      const paramBytes: number[] = [];
      for (let i = 0; i < cleanParams.length; i += 2) {
        paramBytes.push(parseInt(cleanParams.substr(i, 2), 16));
      }
      dataEnvelope = [0x00, command, subCommand, ...paramBytes];
    }

    setGeneratedHex(buildPacket(dataEnvelope));
  }, [command, subCommand, params]);

  const handleSend = () => {
    setIsSending(true);
    setTimeout(() => {
      onSend(generatedHex);
      setIsSending(false);
    }, 400);
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <span className="p-2 bg-indigo-100 text-indigo-600 rounded-lg">🛠️</span>
          Packet Builder
        </h2>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Command</label>
          <select 
            className="w-full p-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-indigo-500 outline-none"
            value={command}
            onChange={(e) => setCommand(Number(e.target.value))}
          >
            {Object.entries(CommandCode)
              .filter(([key]) => isNaN(Number(key)))
              .map(([name, value]) => (
                <option key={value} value={value}>{name}</option>
              ))
            }
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Subcommand</label>
          <select 
            className="w-full p-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-indigo-500 outline-none"
            value={subCommand}
            onChange={(e) => setSubCommand(Number(e.target.value))}
          >
            <option value={SubCommand.SET}>SET (0x01)</option>
            <option value={SubCommand.GET}>GET (0x02)</option>
            <option value={SubCommand.RESPONSE}>RESPONSE (0x10)</option>
          </select>
        </div>
      </div>

      <div className="mb-6">
        <label className="block text-sm font-medium text-slate-700 mb-1">
          {command === CommandCode.LOGIN ? "Credentials (Username|Password)" : "Parameters (Hex)"}
        </label>
        <input 
          type="text"
          className="w-full p-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-indigo-500 outline-none font-mono"
          placeholder={command === CommandCode.LOGIN ? "user|password" : "01 02 FF..."}
          value={params}
          onChange={(e) => setParams(e.target.value)}
        />
      </div>

      <div className="bg-slate-900 text-indigo-400 p-4 rounded-lg relative mb-4">
        <div className="text-xs text-slate-500 mb-1 uppercase tracking-wider font-bold">Generated Hex String</div>
        <code className="text-lg break-all font-mono leading-relaxed">{generatedHex}</code>
      </div>

      <button 
        onClick={handleSend}
        disabled={isSending}
        className={`w-full py-3 rounded-xl font-bold transition-all flex items-center justify-center gap-2 ${
          isSending 
            ? 'bg-slate-100 text-slate-400 cursor-not-allowed' 
            : 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-lg shadow-indigo-100'
        }`}
      >
        {isSending ? (
          <>
            <div className="w-4 h-4 border-2 border-slate-300 border-t-indigo-600 rounded-full animate-spin"></div>
            Transmitting...
          </>
        ) : (
          <>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Send Packet to Device
          </>
        )}
      </button>
    </div>
  );
};

export default PacketBuilder;
