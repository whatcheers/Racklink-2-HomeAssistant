# RackLink Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Home Assistant integration for Middle Atlantic RackLink™ control systems (RLNK-SW715R and compatible models).

## Features

- ✅ **Power Outlet Control** - Control individual power outlets
- ✅ **Sensor Monitoring** - Real-time voltage, current, power, temperature, and more
- ✅ **Real-time Status** - Monitor outlet states and connection status
- ✅ **Auto-discovery** - Automatic outlet discovery and naming
- ✅ **Robust Connection** - Automatic reconnection and error handling
- ✅ **Protocol Compliant** - Full implementation of I-00472 Series Protocol

## Supported Devices

- RLNK-SW715R
- RackLink Select, Premium, and Premium+ models
- Any device supporting the RackLink Control Protocol

## Installation

### HACS (Recommended)

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

### Manual Installation

1. Copy the `custom_components/racklink` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **RackLink**
4. Enter your device details:
   - **Host**: IP address of your RackLink device
   - **Port**: TCP port (default: 60000)
   - **Username**: Login username (default: "user")
   - **Password**: Your device password

## Entities

### Switches
- One switch per power outlet
- Automatically named based on device configuration
- Control outlets on/off directly from Home Assistant

### Sensors
- **Connection Status** - Device connection state
- **Temperature** - Current temperature in Fahrenheit
- **Voltage** - RMS voltage in volts
- **Current** - RMS current in amperes
- **Power** - Power consumption in watts
- **Power Factor** - Power factor measurement
- **Thermal Load** - Thermal load measurement
- **Occupancy** - Occupancy sensor status

## Protocol

This integration implements the RackLink protocol as documented in:
- **I-00472 Series Protocol Manual** (Rev G)

### Supported Commands
- Login (0x02)
- Ping/Pong (0x01) 
- Power Outlets (0x20)
- Outlet Name (0x21)
- Outlet Count (0x22)

## Troubleshooting

### Connection Issues
- Verify the device IP address is correct
- Ensure port 60000 is accessible
- Check that the control protocol is enabled on the device

### Authentication Errors
- For Select/Premium models: Use the "user" account password set via web interface
- For Premium+: Use any admin account with control protocol enabled
- Verify credentials are correct

### Device Not Responding
- Check device network connectivity
- Verify device firmware supports control protocol
- Review Home Assistant logs for detailed error messages

## Development

This integration includes:
- Full protocol implementation
- Standalone CLI tool for testing
- Protocol explorer web application

See the main [README.md](../README.md) for development details.

## Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Check the protocol manual for device-specific details

## License

© 2024 Middle Atlantic. Protocol reference tool and integration.
