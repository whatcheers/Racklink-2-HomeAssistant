
import React, { useState } from 'react';

interface ScriptGeneratorProps {
  hex: string;
}

const ScriptGenerator: React.FC<ScriptGeneratorProps> = ({ hex }) => {
  const [ip, setIp] = useState('192.168.1.100');
  const port = 2000;

  // Clean the hex string for script use
  const cleanHex = hex.replace(/\s/g, '');
  const formattedHexArray = hex.split(' ').map(h => `0x${h}`).join(', ');

  const nodeScript = `
const net = require('net');

const client = new net.Socket();
const IP = '${ip}';
const PORT = ${port};

// Packet for OUTLET_NAME GET
const packet = Buffer.from([${formattedHexArray}]);

client.connect(PORT, IP, () => {
  console.log('Connected to RLNK-SW715R');
  client.write(packet);
});

client.on('data', (data) => {
  console.log('Received Response (Hex):', data.toString('hex').toUpperCase());
  // Basic parsing of response
  if (data.length > 5 && data[3] === 0x21) {
    const name = data.slice(5, data.length - 2).toString();
    console.log('Outlet Name:', name);
  }
  client.destroy(); 
});

client.on('error', (err) => console.error('Connection Error:', err.message));
client.on('close', () => console.log('Connection Closed'));
  `.trim();

  const pythonScript = `
import socket

IP = '${ip}'
PORT = ${port}
# Packet for OUTLET_NAME GET
packet = bytes([${formattedHexArray}])

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((IP, PORT))
        s.sendall(packet)
        data = s.recv(1024)
        print(f"Received (Hex): {data.hex().upper()}")
        
        # Simple extraction if it's an OUTLET_NAME response
        if len(data) > 5 and data[3] == 0x21:
            name = data[5:-2].decode('ascii')
            print(f"Outlet Name: {name}")
except Exception as e:
    print(f"Error: {e}")
  `.trim();

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
          <span className="p-1.5 bg-orange-100 text-orange-600 rounded-lg text-sm">🌐</span>
          Device Configuration
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Device IP Address</label>
            <input 
              type="text" 
              value={ip} 
              onChange={(e) => setIp(e.target.value)}
              className="w-full p-2 bg-slate-50 border border-slate-200 rounded font-mono text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Standard Port</label>
            <input type="text" disabled value={port} className="w-full p-2 bg-slate-100 border border-slate-200 rounded font-mono text-sm text-slate-400" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Node.js Script */}
        <div className="bg-slate-900 rounded-xl overflow-hidden border border-slate-800 flex flex-col">
          <div className="bg-slate-800 px-4 py-2 flex justify-between items-center">
            <span className="text-xs font-bold text-emerald-400 flex items-center gap-2">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M12,2L4.5,20.29L5.21,21L12,18L18.79,21L19.5,20.29L12,2Z" /></svg>
              Node.js (net)
            </span>
            <button onClick={() => copyToClipboard(nodeScript)} className="text-[10px] text-slate-400 hover:text-white uppercase font-bold tracking-widest">Copy Code</button>
          </div>
          <pre className="p-4 text-[11px] font-mono text-slate-300 overflow-x-auto leading-relaxed flex-1">
            {nodeScript}
          </pre>
        </div>

        {/* Python Script */}
        <div className="bg-slate-900 rounded-xl overflow-hidden border border-slate-800 flex flex-col">
          <div className="bg-slate-800 px-4 py-2 flex justify-between items-center">
            <span className="text-xs font-bold text-blue-400 flex items-center gap-2">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12S6.48 22 12 22 22 17.52 22 12 17.52 2 12 2M12 20C7.59 20 4 16.41 4 12S7.59 4 12 4 20 7.59 20 12 16.41 20 12 20Z" /></svg>
              Python (socket)
            </span>
            <button onClick={() => copyToClipboard(pythonScript)} className="text-[10px] text-slate-400 hover:text-white uppercase font-bold tracking-widest">Copy Code</button>
          </div>
          <pre className="p-4 text-[11px] font-mono text-slate-300 overflow-x-auto leading-relaxed flex-1">
            {pythonScript}
          </pre>
        </div>
      </div>
      
      <div className="bg-amber-50 border border-amber-200 p-4 rounded-xl text-amber-800 text-sm">
        <h4 className="font-bold flex items-center gap-2 mb-1">
          <span>⚠️</span> Important Connection Note
        </h4>
        <p className="leading-relaxed">
          The <strong>RLNK-SW715R</strong> only allows a limited number of concurrent TCP connections. If the script fails to connect, ensure you have closed any web browsers or Telnet sessions currently logged into the device's management interface.
        </p>
      </div>
    </div>
  );
};

export default ScriptGenerator;
