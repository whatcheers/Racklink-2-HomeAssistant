#!/usr/bin/env python3
"""Unit tests for RackLink protocol implementation."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.racklink.protocol import RackLinkProtocol
from custom_components.racklink.const import (
    PROTOCOL_HEADER,
    PROTOCOL_TAIL,
    PROTOCOL_ESCAPE,
)


def test_checksum():
    """Test checksum calculation."""
    client = RackLinkProtocol("127.0.0.1")
    
    # Example from protocol manual: Login packet
    # 0xfe 0x10 0x00 0x02 0x01 "user|password" 0x3F 0xff
    header = PROTOCOL_HEADER
    length = 0x10
    data_envelope = [0x00, 0x02, 0x01] + list(b"user|password")
    
    checksum = client._calculate_checksum(header, length, data_envelope)
    print(f"Checksum test: 0x{checksum:02X} (expected: 0x3F)")
    assert checksum == 0x3F, f"Checksum mismatch: got 0x{checksum:02X}, expected 0x3F"
    print("✅ Checksum calculation correct")


def test_escape():
    """Test escape/unescape functionality."""
    client = RackLinkProtocol("127.0.0.1")
    
    # Test escaping protected values
    data = [0xFE, 0x00, 0xFF, 0x01, 0xFD, 0x02]
    escaped = client._escape_data(data)
    unescaped = client._unescape_data(escaped)
    
    print(f"Original: {[hex(b) for b in data]}")
    print(f"Escaped:  {[hex(b) for b in escaped]}")
    print(f"Unescaped: {[hex(b) for b in unescaped]}")
    
    assert unescaped == data, "Escape/unescape failed"
    print("✅ Escape/unescape correct")


def test_packet_build():
    """Test packet building."""
    client = RackLinkProtocol("127.0.0.1")
    
    # Build a simple ping packet
    data_envelope = [0x00, 0x01, 0x01]  # dest=0x00, cmd=PING, sub=SET
    packet = client.build_packet(data_envelope)
    
    print(f"Built packet: {packet.hex(' ').upper()}")
    
    # Verify structure
    assert packet[0] == PROTOCOL_HEADER, "Missing header"
    assert packet[-1] == PROTOCOL_TAIL, "Missing tail"
    assert len(packet) >= 5, "Packet too short"
    
    print("✅ Packet building correct")


def test_packet_parse():
    """Test packet parsing."""
    client = RackLinkProtocol("127.0.0.1")
    
    # Build and parse a packet
    data_envelope = [0x00, 0x01, 0x10]  # dest=0x00, cmd=PING, sub=RESPONSE
    packet = client.build_packet(data_envelope)
    parsed = client.parse_packet(packet)
    
    print(f"Parsed packet: {parsed}")
    
    assert parsed is not None, "Failed to parse packet"
    assert parsed["command"] == 0x01, "Command mismatch"
    assert parsed["subcommand"] == 0x10, "Subcommand mismatch"
    
    print("✅ Packet parsing correct")


def test_login_packet():
    """Test login packet construction."""
    client = RackLinkProtocol("127.0.0.1")
    
    # Build login packet: "user|password"
    login_str = "user|password"
    data_envelope = [0x00, 0x02, 0x01] + list(login_str.encode("ascii"))
    packet = client.build_packet(data_envelope)
    
    print(f"Login packet: {packet.hex(' ').upper()}")
    
    # Parse it back
    parsed = client.parse_packet(packet)
    assert parsed is not None, "Failed to parse login packet"
    assert parsed["command"] == 0x02, "Not a login command"
    
    # Extract login string
    login_bytes = parsed["data"]
    login_reconstructed = bytes(login_bytes).decode("ascii")
    assert login_reconstructed == login_str, "Login string mismatch"
    
    print(f"✅ Login packet: {login_reconstructed}")


if __name__ == "__main__":
    print("Running RackLink Protocol Tests\n")
    print("=" * 50)
    
    try:
        test_checksum()
        print()
        test_escape()
        print()
        test_packet_build()
        print()
        test_packet_parse()
        print()
        test_login_packet()
        print()
        print("=" * 50)
        print("✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
