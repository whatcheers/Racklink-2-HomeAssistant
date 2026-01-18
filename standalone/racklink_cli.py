#!/usr/bin/env python3
"""Standalone RackLink CLI tool for testing protocol without Home Assistant."""
import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import protocol
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.racklink.protocol import RackLinkProtocol
from custom_components.racklink.const import (
    CMD_POWER_OUTLETS,
    CMD_OUTLET_NAME,
    CMD_OUTLET_COUNT,
    CMD_PING,
    SUB_GET,
    SUB_SET,
)


class RackLinkCLI:
    """Interactive CLI for RackLink testing."""

    def __init__(self, host: str, port: int, username: str, password: str):
        """Initialize CLI."""
        self.client = RackLinkProtocol(host, port)
        self.username = username
        self.password = password
        self.connected = False

    async def connect(self) -> bool:
        """Connect and login to device."""
        print(f"Connecting to {self.client.host}:{self.client.port}...")
        if not await self.client.connect():
            print("❌ Connection failed!")
            return False

        print("Logging in...")
        if not await self.client.login(self.username, self.password):
            print("❌ Login failed!")
            await self.client.disconnect()
            return False

        print("✅ Connected and logged in!")
        self.connected = True
        return True

    async def disconnect(self) -> None:
        """Disconnect from device."""
        if self.connected:
            await self.client.disconnect()
            self.connected = False
            print("Disconnected.")

    async def cmd_ping(self) -> None:
        """Test ping/pong."""
        print("Sending ping...")
        if await self.client.ping():
            print("✅ Pong received!")
        else:
            print("❌ Ping failed!")

    async def cmd_outlet_count(self) -> None:
        """Get outlet count."""
        print("Getting outlet count...")
        count = await self.client.get_outlet_count()
        if count is not None:
            print(f"✅ Found {count} outlets")
        else:
            print("❌ Failed to get outlet count")

    async def cmd_outlet_list(self) -> None:
        """List all outlets."""
        count = await self.client.get_outlet_count()
        if count is None:
            print("❌ Could not get outlet count")
            return

        print(f"\n{'Index':<8} {'Name':<30} {'State':<10}")
        print("-" * 50)
        for i in range(1, count + 1):
            state = await self.client.get_outlet_state(i)
            name = await self.client.get_outlet_name(i)
            state_str = "ON" if state else "OFF" if state is not None else "UNKNOWN"
            name_str = name or f"Outlet {i}"
            print(f"{i:<8} {name_str:<30} {state_str:<10}")

    async def cmd_outlet_get(self, index: int) -> None:
        """Get outlet state."""
        print(f"Getting state for outlet {index}...")
        state = await self.client.get_outlet_state(index)
        name = await self.client.get_outlet_name(index)
        if state is not None:
            state_str = "ON" if state else "OFF"
            name_str = name or f"Outlet {index}"
            print(f"✅ {name_str}: {state_str}")
        else:
            print(f"❌ Failed to get state for outlet {index}")

    async def cmd_outlet_set(self, index: int, state: bool) -> None:
        """Set outlet state."""
        state_str = "ON" if state else "OFF"
        print(f"Setting outlet {index} to {state_str}...")
        success = await self.client.set_outlet_state(index, state)
        if success:
            print(f"✅ Outlet {index} set to {state_str}")
        else:
            print(f"❌ Failed to set outlet {index}")

    async def cmd_raw(self, command: int, subcommand: int, data: str = "") -> None:
        """Send raw command."""
        data_bytes = []
        if data:
            # Try to parse as hex first
            if all(c in "0123456789abcdefABCDEF " for c in data):
                clean = data.replace(" ", "")
                for i in range(0, len(clean), 2):
                    if i + 1 < len(clean):
                        data_bytes.append(int(clean[i : i + 2], 16))
            else:
                # Treat as ASCII
                data_bytes = list(data.encode("ascii"))

        print(f"Sending command: 0x{command:02X}, subcommand: 0x{subcommand:02X}")
        if data_bytes:
            print(f"Data: {[hex(b) for b in data_bytes]}")

        response = await self.client.send_command(command, subcommand, data_bytes if data_bytes else None)
        if response:
            print("✅ Response received:")
            print(f"  Command: 0x{response['command']:02X}")
            print(f"  Subcommand: 0x{response['subcommand']:02X}")
            print(f"  Data: {[hex(b) for b in response['data']]}")
            if response["data"]:
                try:
                    ascii_data = bytes(response["data"]).decode("ascii", errors="ignore")
                    print(f"  ASCII: {ascii_data}")
                except:
                    pass
        else:
            print("❌ No response or error")

    async def interactive_shell(self) -> None:
        """Run interactive shell."""
        if not await self.connect():
            return

        print("\n" + "=" * 60)
        print("RackLink Interactive Shell")
        print("=" * 60)
        print("Commands:")
        print("  ping                    - Test ping/pong")
        print("  count                   - Get outlet count")
        print("  list                    - List all outlets")
        print("  get <index>             - Get outlet state")
        print("  on <index>              - Turn outlet ON")
        print("  off <index>             - Turn outlet OFF")
        print("  raw <cmd> <sub> [data]  - Send raw command (hex)")
        print("  help                    - Show this help")
        print("  quit/exit               - Exit")
        print("=" * 60 + "\n")

        while self.connected:
            try:
                line = input("racklink> ").strip()
                if not line:
                    continue

                parts = line.split()
                cmd = parts[0].lower()

                if cmd in ("quit", "exit", "q"):
                    break
                elif cmd == "help":
                    print("Commands: ping, count, list, get <n>, on <n>, off <n>, raw <cmd> <sub> [data], quit")
                elif cmd == "ping":
                    await self.cmd_ping()
                elif cmd == "count":
                    await self.cmd_outlet_count()
                elif cmd == "list":
                    await self.cmd_outlet_list()
                elif cmd == "get" and len(parts) > 1:
                    await self.cmd_outlet_get(int(parts[1]))
                elif cmd == "on" and len(parts) > 1:
                    await self.cmd_outlet_set(int(parts[1]), True)
                elif cmd == "off" and len(parts) > 1:
                    await self.cmd_outlet_set(int(parts[1]), False)
                elif cmd == "raw" and len(parts) >= 3:
                    cmd_byte = int(parts[1], 16) if parts[1].startswith("0x") else int(parts[1], 16)
                    sub_byte = int(parts[2], 16) if parts[2].startswith("0x") else int(parts[2], 16)
                    data = " ".join(parts[3:]) if len(parts) > 3 else ""
                    await self.cmd_raw(cmd_byte, sub_byte, data)
                else:
                    print("Unknown command. Type 'help' for help.")

            except KeyboardInterrupt:
                print("\nInterrupted.")
                break
            except Exception as e:
                print(f"Error: {e}")

        await self.disconnect()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="RackLink Protocol CLI Tool")
    parser.add_argument("host", help="RackLink device IP address")
    parser.add_argument("-p", "--port", type=int, default=60000, help="TCP port (default: 60000)")
    parser.add_argument("-u", "--username", default="user", help="Username (default: user)")
    parser.add_argument("-P", "--password", required=True, help="Password")
    parser.add_argument("-c", "--command", help="Single command to execute (ping, count, list, get <n>, on <n>, off <n>)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run interactive shell")

    args = parser.parse_args()

    cli = RackLinkCLI(args.host, args.port, args.username, args.password)

    if args.interactive or not args.command:
        await cli.interactive_shell()
    else:
        # Single command mode
        if not await cli.connect():
            sys.exit(1)

        try:
            cmd_parts = args.command.split()
            cmd = cmd_parts[0].lower()

            if cmd == "ping":
                await cli.cmd_ping()
            elif cmd == "count":
                await cli.cmd_outlet_count()
            elif cmd == "list":
                await cli.cmd_outlet_list()
            elif cmd == "get" and len(cmd_parts) > 1:
                await cli.cmd_outlet_get(int(cmd_parts[1]))
            elif cmd == "on" and len(cmd_parts) > 1:
                await cli.cmd_outlet_set(int(cmd_parts[1]), True)
            elif cmd == "off" and len(cmd_parts) > 1:
                await cli.cmd_outlet_set(int(cmd_parts[1]), False)
            else:
                print(f"Unknown command: {args.command}")
                print("Available: ping, count, list, get <n>, on <n>, off <n>")
                sys.exit(1)
        finally:
            await cli.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
