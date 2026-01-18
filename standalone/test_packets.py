#!/usr/bin/env python3
"""Test packet building against protocol manual specifications."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.racklink.protocol import RackLinkProtocol
from custom_components.racklink.const import (
    CMD_OUTLET_COUNT,
    CMD_OUTLET_NAME,
    CMD_POWER_OUTLETS,
    SUB_GET,
    PROTOCOL_HEADER,
    PROTOCOL_TAIL,
)


def test_outlet_count_packet():
    """Test outlet count GET packet format per protocol manual."""
    client = RackLinkProtocol("127.0.0.1")
    
    # Per protocol manual: Outlet Count GET
    # Data envelope: [0x00, 0x22, 0x02]
    # 0x00 = destination
    # 0x22 = CMD_OUTLET_COUNT
    # 0x02 = SUB_GET
    data_envelope = [0x00, CMD_OUTLET_COUNT, SUB_GET]
    packet = client.build_packet(data_envelope)
    
    print("=" * 60)
    print("Outlet Count GET Packet")
    print("=" * 60)
    print(f"Data envelope: {[hex(b) for b in data_envelope]}")
    print(f"Full packet: {packet.hex(' ').upper()}")
    print(f"Expected format: FE [length] 00 22 02 [checksum] FF")
    print()
    
    # Verify structure
    assert packet[0] == PROTOCOL_HEADER, "Header should be 0xFE"
    assert packet[-1] == PROTOCOL_TAIL, "Tail should be 0xFF"
    assert len(packet) >= 5, "Packet too short"
    
    # Parse it back
    parsed = client.parse_packet(packet)
    if parsed:
        print("Parsed back:")
        print(f"  Destination: 0x{parsed['destination']:02X}")
        print(f"  Command: 0x{parsed['command']:02X} (should be 0x22)")
        print(f"  Subcommand: 0x{parsed['subcommand']:02X} (should be 0x02)")
        assert parsed['command'] == CMD_OUTLET_COUNT
        assert parsed['subcommand'] == SUB_GET
        print("✅ Packet format correct")
    else:
        print("❌ Failed to parse packet")
        return False
    
    return True


def test_outlet_name_packet():
    """Test outlet name GET packet format per protocol manual."""
    client = RackLinkProtocol("127.0.0.1")
    
    # Per protocol manual: Outlet Name GET for outlet 1
    # Data envelope: [0x00, 0x21, 0x02, 0x01]
    # 0x00 = destination
    # 0x21 = CMD_OUTLET_NAME
    # 0x02 = SUB_GET
    # 0x01 = outlet index (1)
    outlet_index = 1
    data_envelope = [0x00, CMD_OUTLET_NAME, SUB_GET, outlet_index]
    packet = client.build_packet(data_envelope)
    
    print("=" * 60)
    print("Outlet Name GET Packet (Outlet 1)")
    print("=" * 60)
    print(f"Data envelope: {[hex(b) for b in data_envelope]}")
    print(f"Full packet: {packet.hex(' ').upper()}")
    print(f"Expected format: FE [length] 00 21 02 01 [checksum] FF")
    print()
    
    parsed = client.parse_packet(packet)
    if parsed:
        print("Parsed back:")
        print(f"  Destination: 0x{parsed['destination']:02X}")
        print(f"  Command: 0x{parsed['command']:02X} (should be 0x21)")
        print(f"  Subcommand: 0x{parsed['subcommand']:02X} (should be 0x02)")
        print(f"  Data: {[hex(b) for b in parsed['data']]} (should be [0x01])")
        assert parsed['command'] == CMD_OUTLET_NAME
        assert parsed['subcommand'] == SUB_GET
        assert parsed['data'] == [outlet_index]
        print("✅ Packet format correct")
    else:
        print("❌ Failed to parse packet")
        return False
    
    return True


def test_power_outlet_get_packet():
    """Test power outlet GET packet format per protocol manual."""
    client = RackLinkProtocol("127.0.0.1")
    
    # Per protocol manual: Power Outlet GET for outlet 1
    # Data envelope: [0x00, 0x20, 0x02, 0x01]
    # 0x00 = destination
    # 0x20 = CMD_POWER_OUTLETS
    # 0x02 = SUB_GET
    # 0x01 = outlet index (1)
    outlet_index = 1
    data_envelope = [0x00, CMD_POWER_OUTLETS, SUB_GET, outlet_index]
    packet = client.build_packet(data_envelope)
    
    print("=" * 60)
    print("Power Outlet GET Packet (Outlet 1)")
    print("=" * 60)
    print(f"Data envelope: {[hex(b) for b in data_envelope]}")
    print(f"Full packet: {packet.hex(' ').upper()}")
    print(f"Expected format: FE [length] 00 20 02 01 [checksum] FF")
    print()
    
    parsed = client.parse_packet(packet)
    if parsed:
        print("Parsed back:")
        print(f"  Destination: 0x{parsed['destination']:02X}")
        print(f"  Command: 0x{parsed['command']:02X} (should be 0x20)")
        print(f"  Subcommand: 0x{parsed['subcommand']:02X} (should be 0x02)")
        print(f"  Data: {[hex(b) for b in parsed['data']]} (should be [0x01])")
        assert parsed['command'] == CMD_POWER_OUTLETS
        assert parsed['subcommand'] == SUB_GET
        assert parsed['data'] == [outlet_index]
        print("✅ Packet format correct")
    else:
        print("❌ Failed to parse packet")
        return False
    
    return True


def show_protocol_reference():
    """Show expected packet formats from protocol manual."""
    print("=" * 60)
    print("Protocol Manual Reference")
    print("=" * 60)
    print()
    print("Packet Structure:")
    print("  [Header] [Length] [Data Envelope] [Checksum] [Tail]")
    print("  [0xFE]   [len]    [escaped]       [7-bit]   [0xFF]")
    print()
    print("Outlet Count GET (0x22):")
    print("  Data Envelope: [0x00, 0x22, 0x02]")
    print("  Expected Response: [0x00, 0x22, 0x10, count_byte]")
    print()
    print("Outlet Name GET (0x21):")
    print("  Data Envelope: [0x00, 0x21, 0x02, outlet_index]")
    print("  Expected Response: [0x00, 0x21, 0x10, outlet_index, name_bytes...]")
    print()
    print("Power Outlet GET (0x20):")
    print("  Data Envelope: [0x00, 0x20, 0x02, outlet_index]")
    print("  Expected Response: [0x00, 0x20, 0x10, outlet_index, state_byte]")
    print()


if __name__ == "__main__":
    print("RackLink Protocol Packet Format Verification")
    print("=" * 60)
    print()
    
    show_protocol_reference()
    print()
    
    try:
        test_outlet_count_packet()
        print()
        test_outlet_name_packet()
        print()
        test_power_outlet_get_packet()
        print()
        print("=" * 60)
        print("✅ All packet format tests passed!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
