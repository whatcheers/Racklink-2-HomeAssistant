# RackLink Standalone CLI Tool

A standalone command-line tool for testing RackLink protocol communication without Home Assistant.

## Installation

No special installation required - just Python 3.7+ with asyncio support (standard library).

## Usage

### Interactive Mode

Run an interactive shell to test commands:

```bash
python3 racklink_cli.py <host> -P <password> [options]
```

Example:
```bash
python3 racklink_cli.py 192.168.1.100 -P mypassword
```

Options:
- `-p, --port PORT` - TCP port (default: 60000)
- `-u, --username USERNAME` - Username (default: "user")
- `-P, --password PASSWORD` - Password (required)
- `-i, --interactive` - Run interactive shell (default if no command specified)

### Single Command Mode

Execute a single command and exit:

```bash
python3 racklink_cli.py <host> -P <password> -c "<command>"
```

Available commands:
- `ping` - Test ping/pong
- `count` - Get outlet count
- `list` - List all outlets with states
- `get <n>` - Get state of outlet N
- `on <n>` - Turn outlet N ON
- `off <n>` - Turn outlet N OFF

Examples:
```bash
# Test connection
python3 racklink_cli.py 192.168.1.100 -P mypassword -c "ping"

# Get outlet count
python3 racklink_cli.py 192.168.1.100 -P mypassword -c "count"

# List all outlets
python3 racklink_cli.py 192.168.1.100 -P mypassword -c "list"

# Get outlet 1 state
python3 racklink_cli.py 192.168.1.100 -P mypassword -c "get 1"

# Turn outlet 1 ON
python3 racklink_cli.py 192.168.1.100 -P mypassword -c "on 1"

# Turn outlet 1 OFF
python3 racklink_cli.py 192.168.1.100 -P mypassword -c "off 1"
```

## Interactive Shell Commands

When running in interactive mode, you can use:

- `ping` - Test ping/pong
- `count` - Get outlet count
- `list` - List all outlets
- `get <index>` - Get outlet state
- `on <index>` - Turn outlet ON
- `off <index>` - Turn outlet OFF
- `raw <cmd> <sub> [data]` - Send raw hex command
- `help` - Show help
- `quit` / `exit` - Exit shell

### Raw Command Example

Send a raw protocol command:
```
racklink> raw 0x20 0x02 01
```

This sends:
- Command: 0x20 (Power Outlets)
- Subcommand: 0x02 (GET)
- Data: 0x01 (Outlet 1)

## Examples

### Basic Testing Workflow

```bash
# 1. Connect and test ping
python3 racklink_cli.py 192.168.1.100 -P mypassword -c "ping"

# 2. Check how many outlets
python3 racklink_cli.py 192.168.1.100 -P mypassword -c "count"

# 3. List all outlets
python3 racklink_cli.py 192.168.1.100 -P mypassword -c "list"

# 4. Control an outlet
python3 racklink_cli.py 192.168.1.100 -P mypassword -c "on 1"
python3 racklink_cli.py 192.168.1.100 -P mypassword -c "off 1"
```

### Interactive Session

```bash
$ python3 racklink_cli.py 192.168.1.100 -P mypassword

Connecting to 192.168.1.100:60000...
Logging in...
✅ Connected and logged in!

============================================================
RackLink Interactive Shell
============================================================
Commands:
  ping                    - Test ping/pong
  count                   - Get outlet count
  list                    - List all outlets
  get <index>             - Get outlet state
  on <index>              - Turn outlet ON
  off <index>             - Turn outlet OFF
  raw <cmd> <sub> [data]  - Send raw command (hex)
  help                    - Show this help
  quit/exit               - Exit
============================================================

racklink> ping
Sending ping...
✅ Pong received!
racklink> count
Getting outlet count...
✅ Found 8 outlets
racklink> list

Index    Name                           State     
--------------------------------------------------
1        Outlet 1                       ON        
2        Outlet 2                       OFF       
3        Outlet 3                       ON        
...
racklink> off 1
Setting outlet 1 to OFF...
✅ Outlet 1 set to OFF
racklink> quit
Disconnected.
```

## Diagnostic Tool

For troubleshooting connection issues, use the diagnostic tool:

```bash
python3 standalone/diagnose.py <host> -P <password>
```

This will run a series of tests:
- TCP connection
- Login authentication
- Initial ping handling
- Ping/Pong
- Outlet count
- Outlet states
- Raw command testing

Example output:
```bash
$ python3 standalone/diagnose.py 192.168.1.252 -P mypassword

============================================================
RackLink RLNK-SW715R Diagnostic Tool
============================================================
Host: 192.168.1.252:60000
Username: user

Test 1: TCP Connection
------------------------------------------------------------
✅ TCP connection successful

Test 2: Login
------------------------------------------------------------
✅ Login successful

Test 3: Initial Ping from Device
------------------------------------------------------------
✅ Device sent ping (SET)
✅ Sent pong response
...
```

## Troubleshooting

- **Connection refused**: Check IP address and port (default 60000)
- **Login failed**: Verify username and password are correct
- **Timeout errors**: Ensure device is accessible on network
- **Protocol errors**: Check that control protocol is enabled on device
- **RLNK-SW715R specific**: Run the diagnostic tool to identify specific issues

## Protocol Reference

This tool uses the same protocol implementation as the Home Assistant integration, based on:
- **I-00472 Series Protocol Manual** (Rev G)

See the main README.md for protocol details.
