
import { CommandCode, SubCommand, ProtocolPacket, PacketBreakdown } from '../types';

export const PROTECTED_VALUES = {
  HEADER: 0xFE,
  TAIL: 0xFF,
  ESCAPE: 0xFD
};

export const calculateChecksum = (header: number, length: number, data: number[]): number => {
  let sum = header + length;
  for (const byte of data) {
    sum += byte;
  }
  return sum & 0x7F;
};

export const escapeData = (data: number[]): number[] => {
  const escaped: number[] = [];
  for (const byte of data) {
    if (Object.values(PROTECTED_VALUES).includes(byte)) {
      escaped.push(PROTECTED_VALUES.ESCAPE);
      escaped.push((~byte) & 0xFF);
    } else {
      escaped.push(byte);
    }
  }
  return escaped;
};

export const unescapeData = (data: number[]): { unescaped: number[], breakdown: boolean[] } => {
  const unescaped: number[] = [];
  const isEscaped: boolean[] = [];
  for (let i = 0; i < data.length; i++) {
    if (data[i] === PROTECTED_VALUES.ESCAPE && i + 1 < data.length) {
      unescaped.push((~data[i + 1]) & 0xFF);
      isEscaped.push(true);
      i++;
    } else {
      unescaped.push(data[i]);
      isEscaped.push(false);
    }
  }
  return { unescaped, breakdown: isEscaped };
};

export const hexToBytes = (hex: string): number[] => {
  const cleanHex = hex.replace(/[^0-9a-fA-F]/g, '');
  const bytes: number[] = [];
  for (let i = 0; i < cleanHex.length; i += 2) {
    bytes.push(parseInt(cleanHex.substr(i, 2), 16));
  }
  return bytes;
};

export const bytesToHex = (bytes: number[]): string => {
  return bytes.map(b => b.toString(16).padStart(2, '0').toUpperCase()).join(' ');
};

export const asciiToBytes = (str: string): number[] => {
  return Array.from(str).map(char => char.charCodeAt(0));
};

export const buildPacket = (dataEnvelope: number[]): string => {
  const header = PROTECTED_VALUES.HEADER;
  const tail = PROTECTED_VALUES.TAIL;
  const length = dataEnvelope.length;
  const checksum = calculateChecksum(header, length, dataEnvelope);
  const escapedEnvelope = escapeData(dataEnvelope);
  const packetBytes = [header, length, ...escapedEnvelope, checksum, tail];
  return bytesToHex(packetBytes);
};

export const simulateResponse = (requestHex: string): string | null => {
  const bytes = hexToBytes(requestHex);
  if (bytes.length < 5) return null;

  const envelopeWithEscapes = bytes.slice(2, bytes.length - 2);
  const { unescaped } = unescapeData(envelopeWithEscapes);
  
  if (unescaped.length < 3) return null;

  const dest = unescaped[0];
  const cmd = unescaped[1];
  const sub = unescaped[2];

  let responseEnvelope: number[] = [0x00, cmd, SubCommand.RESPONSE];

  switch (cmd) {
    case CommandCode.LOGIN:
      responseEnvelope.push(0x01); // 01 = Success
      break;
    case CommandCode.OUTLET_NAME:
      if (sub === SubCommand.GET) {
        // Return "Outlet 1"
        responseEnvelope.push(unescaped[3] || 0x01); // Index
        responseEnvelope.push(...asciiToBytes("Outlet 1"));
      }
      break;
    case CommandCode.POWER_OUTLETS:
      responseEnvelope.push(unescaped[3] || 0x01); // Index
      responseEnvelope.push(0x01); // 01 = ON
      break;
    case CommandCode.PING:
      responseEnvelope = [0x00, CommandCode.PING, SubCommand.RESPONSE];
      break;
    default:
      return null;
  }

  return buildPacket(responseEnvelope);
};

export const parsePacket = (hex: string): PacketBreakdown[] => {
  const bytes = hexToBytes(hex);
  if (bytes.length < 5) return [];

  const result: PacketBreakdown[] = [];
  result.push({ label: 'Header', hex: bytesToHex([bytes[0]]), description: bytes[0] === PROTECTED_VALUES.HEADER ? 'Valid Start Character (0xFE)' : 'INVALID Header' });
  const rawLength = bytes[1];
  result.push({ label: 'Length', hex: bytesToHex([bytes[1]]), description: `Payload Data Length: ${rawLength} bytes` });
  const envelopeWithEscapes = bytes.slice(2, bytes.length - 2);
  const { unescaped } = unescapeData(envelopeWithEscapes);
  result.push({ label: 'Data Envelope', hex: bytesToHex(envelopeWithEscapes), description: `Unescaped Payload: [${bytesToHex(unescaped)}]` });

  if (unescaped.length >= 2) {
    const dest = unescaped[0];
    const cmd = unescaped[1];
    const sub = unescaped[2];
    result.push({ label: 'Destination', hex: bytesToHex([dest]), description: dest === 0 ? 'Broadcast/Device' : `Target ${dest}` });
    const cmdName = CommandCode[cmd] || 'Unknown Command';
    result.push({ label: 'Command', hex: bytesToHex([cmd]), description: `${cmdName} (0x${cmd.toString(16).padStart(2, '0')})` });
    if (sub !== undefined) {
      const subName = SubCommand[sub] || 'Param/Data';
      result.push({ label: 'Subcommand/Param', hex: bytesToHex([sub]), description: `${subName}` });
    }
  }

  const checksum = bytes[bytes.length - 2];
  const expectedChecksum = calculateChecksum(bytes[0], rawLength, unescaped);
  result.push({ label: 'Checksum', hex: bytesToHex([checksum]), description: checksum === expectedChecksum ? 'Valid Checksum' : `Invalid! Expected 0x${expectedChecksum.toString(16).toUpperCase()}` });
  const tail = bytes[bytes.length - 1];
  result.push({ label: 'Tail', hex: bytesToHex([tail]), description: tail === PROTECTED_VALUES.TAIL ? 'Valid End Character (0xFF)' : 'INVALID Tail' });

  return result;
};
