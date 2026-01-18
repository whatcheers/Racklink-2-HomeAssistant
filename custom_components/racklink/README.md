# RackLink Home Assistant Integration

Home Assistant custom integration for Middle Atlantic RackLink™ control systems.

## Features

- **Power Outlet Control**: Control individual power outlets on your RackLink device
- **Real-time Monitoring**: Monitor connection status and device state
- **Protocol Implementation**: Full implementation of the RackLink protocol (I-00472 Series Protocol Manual)

## Installation

1. Copy the `racklink` folder to your Home Assistant `custom_components` directory:
   ```
   <config>/custom_components/racklink/
   ```

2. Restart Home Assistant

3. Go to **Settings** → **Devices & Services** → **Add Integration**

4. Search for "RackLink" and follow the setup wizard

## Configuration

During setup, you'll need to provide:
- **Host**: IP address of your RackLink device
- **Port**: TCP port (default: 60000)
- **Username**: Login username (default: "user")
- **Password**: Login password

## Protocol Reference

This integration implements the RackLink protocol as documented in:
- **I-00472 Series Protocol Manual** (Rev G)

### Supported Commands

- Login (0x02)
- Ping/Pong (0x01)
- Power Outlets (0x20)
- Outlet Name (0x21)
- Outlet Count (0x22)
- Sensor Values (0x50-0x61) - *Coming soon*

## Entities

### Switches
- One switch entity per power outlet
- Named according to outlet configuration on device

### Sensors
- Connection status sensor

## Protocol Details

The RackLink protocol uses:
- **Header**: 0xFE
- **Tail**: 0xFF
- **Escape**: 0xFD
- **Checksum**: 7-bit sum of header + length + data envelope
- **Transport**: TCP/IP on port 60000

Protected values (0xFE, 0xFF, 0xFD) are escaped by prefixing with 0xFD followed by the bit-inverted value.

## Troubleshooting

- **Connection Issues**: Ensure the RackLink device is accessible on your network and port 60000 is open
- **Authentication Errors**: Verify your username and password are correct. For Select/Premium models, use the "user" account password set via web interface
- **Protocol Errors**: Check that the device firmware supports the control protocol (enabled by default after first login)

## Development

This integration is based on the protocol explorer tool and implements the full RackLink protocol specification.
