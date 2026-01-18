
export enum CommandCode {
  PING = 0x01,
  LOGIN = 0x02,
  NACK = 0x10,
  POWER_OUTLETS = 0x20,
  OUTLET_NAME = 0x21,
  OUTLET_COUNT = 0x22,
  ENERGY_MGMT = 0x23,
  DRY_CONTACTS = 0x30,
  CONTACT_NAME = 0x31,
  CONTACT_COUNT = 0x32,
  SEQUENCE = 0x36,
  EPO = 0x37,
  LOG_ALERTS = 0x40,
  STATUS_CHANGE = 0x41,
  SENSORS_START = 0x50,
  SENSORS_END = 0x61,
  THRESHOLDS_START = 0x70,
  THRESHOLDS_END = 0x77,
  READ_LOG = 0x80,
  LOG_COUNT = 0x81,
  CLEAR_LOG = 0x82,
  PRODUCT_PART = 0x90,
  PRODUCT_RATING = 0x91,
  PRODUCT_SURGE = 0x93,
  PRODUCT_IP = 0x94,
  PRODUCT_MAC = 0x95
}

export enum SubCommand {
  SET = 0x01,
  GET = 0x02,
  RESPONSE = 0x10,
  STATUS_UPDATE = 0x12,
  LOG_UPDATE = 0x30
}

export interface ProtocolPacket {
  header: number;
  length: number;
  data: number[];
  checksum: number;
  tail: number;
  originalHex?: string;
}

export interface PacketBreakdown {
  label: string;
  hex: string;
  description: string;
  isEscaped?: boolean;
}

export interface LogEntry {
  id: string;
  timestamp: Date;
  direction: 'TX' | 'RX';
  hex: string;
  summary: string;
}
