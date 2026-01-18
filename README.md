# RackLink Protocol Tools & Home Assistant Integration

A comprehensive toolkit for working with Middle Atlantic RackLink™ control systems, including a protocol explorer web application and a Home Assistant custom integration.

## 📋 Project Overview

This repository contains:

1. **Protocol Explorer** - A React-based web tool for building, parsing, and understanding RackLink protocol packets
2. **Home Assistant Integration** - A custom component for controlling RackLink devices from Home Assistant
3. **Standalone CLI Tool** - Command-line tool for testing RackLink protocol without Home Assistant

## 🔧 Protocol Explorer (Web App)

A developer tool for building, parsing, and understanding the RackLink protocol.

### Features

- **Packet Builder**: Visual tool to construct RackLink protocol packets
- **Packet Parser**: Real-time parser to decode and understand protocol packets  
- **AI Consultant**: Gemini-powered assistant trained on the protocol manual
- **Script Generator**: Generate code snippets for deployment
- **Communication Console**: Activity log showing TX/RX packets

### Run Locally

**Prerequisites:** Node.js

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set the `GEMINI_API_KEY` in `.env.local` to your Gemini API key (optional, for AI assistant)

3. Run the app:
   ```bash
   npm run dev
   ```

4. Open your browser to the local development server (typically `http://localhost:5173`)

View your app in AI Studio: https://ai.studio/apps/drive/1Qr2AW-rRan2B1QU0h495bzDPbJZuBjMV

## 🏠 Home Assistant Integration

A custom integration for controlling RackLink devices from Home Assistant.

### Installation via HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the three dots (⋮) in the top right
4. Select **Custom repositories**
5. Add this repository:
   - Repository: `https://github.com/whatcheer/Racklink-2-HomeAssistant`
   - Category: **Integration**
6. Click **Add**
7. Search for "RackLink" in HACS
8. Click **Download**
9. Restart Home Assistant
10. Go to **Settings** → **Devices & Services** → **Add Integration**
11. Search for "RackLink" and follow the setup wizard

### Manual Installation

1. Copy the `custom_components/racklink` folder to your Home Assistant `custom_components` directory:
   ```
   <config>/custom_components/racklink/
   ```

2. Restart Home Assistant

3. Go to **Settings** → **Devices & Services** → **Add Integration**

4. Search for "RackLink" and follow the setup wizard

### Configuration

During setup, provide:
- **Host**: IP address of your RackLink device
- **Port**: TCP port (default: 60000)
- **Username**: Login username (default: "user")
- **Password**: Login password

### Features

- **Power Outlet Control**: Control individual power outlets
- **Real-time Monitoring**: Monitor connection status
- **Automatic Reconnection**: Handles connection drops and reconnects automatically

See [custom_components/racklink/README.md](custom_components/racklink/README.md) for detailed documentation.

## 🖥️ Standalone CLI Tool

A command-line tool for testing RackLink devices without Home Assistant. Perfect for debugging and protocol testing.

### Quick Start

```bash
# Interactive mode
python3 standalone/racklink_cli.py <host> -P <password>

# Single command
python3 standalone/racklink_cli.py <host> -P <password> -c "ping"
python3 standalone/racklink_cli.py <host> -P <password> -c "list"
python3 standalone/racklink_cli.py <host> -P <password> -c "on 1"
```

### Features

- **Interactive Shell**: Test commands interactively
- **Single Command Mode**: Execute commands from command line
- **Raw Protocol Access**: Send custom hex commands
- **No Dependencies**: Uses only Python standard library

See [standalone/README.md](standalone/README.md) for full documentation.

### Protocol Tests

Run unit tests to verify protocol implementation:

```bash
python3 standalone/test_protocol.py
```

## 📚 Protocol Reference

This project implements the RackLink protocol as documented in:
- **I-00472 Series Protocol Manual** (Rev G)

### Protocol Details

- **Header**: 0xFE
- **Tail**: 0xFF  
- **Escape**: 0xFD
- **Checksum**: 7-bit sum (sum & 0x7F)
- **Transport**: TCP/IP on port 60000 (RS-232 also supported on Premium models)

Protected values (0xFE, 0xFF, 0xFD) must be escaped by prefixing with 0xFD followed by the bit-inverted value.

## 🏗️ Project Structure

```
Racklink-2-HomeAssistant/
├── custom_components/          # Home Assistant integration
│   └── racklink/
│       ├── __init__.py         # Integration entry point
│       ├── config_flow.py       # Configuration UI
│       ├── coordinator.py       # Data update coordinator
│       ├── protocol.py          # Protocol implementation
│       ├── switch.py            # Power outlet switches
│       ├── sensor.py            # Sensor entities
│       └── manifest.json        # Integration metadata
├── standalone/                  # Standalone CLI tool
│   ├── racklink_cli.py         # Interactive CLI
│   ├── test_protocol.py         # Protocol unit tests
│   └── README.md                # CLI documentation
├── components/                  # React components
│   ├── PacketBuilder.tsx
│   ├── PacketParser.tsx
│   ├── GeminiAssistant.tsx
│   └── ScriptGenerator.tsx
├── utils/                       # Protocol utilities
│   └── protocolUtils.ts
├── I-00472-Series-Protocol.pdf  # Protocol reference manual
└── README.md                    # This file
```

## 📝 License

© 2024 Middle Atlantic. Protocol reference tool and integration.

## 🔗 Resources

- [Middle Atlantic Products](https://www.middleatlantic.com/)
- Protocol Manual: I-00472 Series (Rev G)
