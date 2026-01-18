#!/usr/bin/env python3
"""Diagnostic tool for RLNK-SW715R troubleshooting."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.racklink.protocol import RackLinkProtocol
from custom_components.racklink.const import (
    CMD_POWER_OUTLETS,
    CMD_OUTLET_NAME,
    CMD_OUTLET_COUNT,
    CMD_PING,
    CMD_NACK,
    SUB_GET,
    SUB_SET,
    SUB_RESPONSE,
)


async def diagnose(host: str, port: int, username: str, password: str):
    """Run diagnostic tests."""
    print("=" * 60)
    print("RackLink RLNK-SW715R Diagnostic Tool")
    print("=" * 60)
    print(f"Host: {host}:{port}")
    print(f"Username: {username}")
    print()

    client = RackLinkProtocol(host, port)

    # Test 1: Connection
    print("Test 1: TCP Connection")
    print("-" * 60)
    if await client.connect():
        print("✅ TCP connection successful")
    else:
        print("❌ TCP connection failed")
        return
    print()

    # Test 2: Login
    print("Test 2: Login")
    print("-" * 60)
    login_str = f"{username}|{password}"
    data_envelope = [0x00, 0x02, 0x01] + list(login_str.encode("ascii"))
    packet = client.build_packet(data_envelope)
    print(f"Login packet: {packet.hex(' ').upper()}")
    
    await client.send_packet(packet)
    response = await client.receive_packet(timeout=5.0)
    
    if response:
        print(f"Response: cmd=0x{response['command']:02X}, sub=0x{response['subcommand']:02X}")
        print(f"Data: {[hex(b) for b in response['data']]}")
        
        if response["command"] == 0x10:  # NACK
            error_code = response["data"][0] if response["data"] else 0
            print(f"❌ Login NACK, error code: 0x{error_code:02X}")
            await client.disconnect()
            return
        elif response["command"] == 0x02 and response["subcommand"] == 0x10:
            if response["data"] and response["data"][0] == 0x01:
                print("✅ Login successful")
            else:
                print("❌ Login response indicates failure")
                await client.disconnect()
                return
        else:
            print(f"⚠️  Unexpected response")
    else:
        print("❌ No response to login")
        await client.disconnect()
        return
    
    # Test 3: Initial Ping (device sends ping after login)
    print()
    print("Test 3: Initial Ping from Device")
    print("-" * 60)
    ping_response = await client.receive_packet(timeout=5.0)
    if ping_response:
        print(f"Received: cmd=0x{ping_response['command']:02X}, sub=0x{ping_response['subcommand']:02X}")
        if ping_response["command"] == 0x01 and ping_response["subcommand"] == 0x01:
            print("✅ Device sent ping (SET)")
            # Respond with pong
            pong_envelope = [0x00, 0x01, 0x10]
            pong_packet = client.build_packet(pong_envelope)
            await client.send_packet(pong_packet)
            print("✅ Sent pong response")
        else:
            print(f"⚠️  Expected ping, got: cmd=0x{ping_response['command']:02X}")
    else:
        print("⚠️  No ping received (may be normal for some devices)")
    print()

    # Test 4: Ping/Pong
    print("Test 4: Ping/Pong (Client-initiated)")
    print("-" * 60)
    ping_result = await client.ping()
    if ping_result:
        print("✅ Ping/Pong successful")
    else:
        print("⚠️  Ping/Pong failed (device may not support client-initiated pings)")
        print("   This is normal - device sends pings, we respond. Testing with real command...")
    print()

    # Test 5: Outlet Count
    print("Test 5: Get Outlet Count")
    print("-" * 60)
    count = await client.get_outlet_count()
    if count is not None:
        print(f"✅ Outlet count: {count}")
    else:
        print("❌ Failed to get outlet count")
        # Try raw command
        print("Trying raw command...")
        response = await client.send_command(0x22, 0x02)
        if response:
            print(f"Raw response: {response}")
    print()

    # Test 6: Get Outlet States
    print("Test 6: Get Outlet States")
    print("-" * 60)
    if count:
        for i in range(1, min(count + 1, 9)):  # Test first 8
            state = await client.get_outlet_state(i)
            name = await client.get_outlet_name(i)
            if state is not None:
                print(f"  Outlet {i}: {name or f'Outlet {i}'} - {'ON' if state else 'OFF'}")
            else:
                print(f"  Outlet {i}: Failed to get state")
    print()

    # Test 7: Raw Command Test
    print("Test 7: Raw Command (Get Outlet 1)")
    print("-" * 60)
    response = await client.send_command(CMD_POWER_OUTLETS, SUB_GET, [1])
    if response:
        print(f"✅ Response: {response}")
        print(f"   Command: 0x{response['command']:02X}")
        print(f"   Subcommand: 0x{response['subcommand']:02X}")
        print(f"   Data: {[hex(b) for b in response['data']]}")
    else:
        print("❌ No response")
    print()

    await client.disconnect()
    print("=" * 60)
    print("Diagnostics complete")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="RackLink Diagnostic Tool")
    parser.add_argument("host", help="RackLink device IP")
    parser.add_argument("-p", "--port", type=int, default=60000, help="Port (default: 60000)")
    parser.add_argument("-u", "--username", default="user", help="Username (default: user)")
    parser.add_argument("-P", "--password", required=True, help="Password")
    
    args = parser.parse_args()
    
    asyncio.run(diagnose(args.host, args.port, args.username, args.password))
