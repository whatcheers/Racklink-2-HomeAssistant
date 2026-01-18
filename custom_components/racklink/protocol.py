"""RackLink Protocol Implementation based on I-00472 Series Protocol Manual."""
from __future__ import annotations

import asyncio
import logging
import socket
from typing import Any

from .const import (
    CMD_LOGIN,
    CMD_NACK,
    CMD_OUTLET_COUNT,
    CMD_OUTLET_NAME,
    CMD_PING,
    CMD_POWER_OUTLETS,
    PROTOCOL_ESCAPE,
    PROTOCOL_HEADER,
    PROTOCOL_PORT,
    PROTOCOL_TAIL,
    SUB_GET,
    SUB_RESPONSE,
    SUB_SET,
)

_LOGGER = logging.getLogger(__name__)


class RackLinkProtocol:
    """RackLink Protocol client implementation."""

    def __init__(self, host: str, port: int = PROTOCOL_PORT) -> None:
        """Initialize the protocol client."""
        self.host = host
        self.port = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._connected = False
        self._ping_task: asyncio.Task | None = None

    async def connect(self) -> bool:
        """Connect to the RackLink device."""
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port), timeout=5.0
            )
            self._connected = True
            _LOGGER.info("Connected to RackLink device at %s:%d", self.host, self.port)
            return True
        except (asyncio.TimeoutError, OSError) as err:
            _LOGGER.error("Failed to connect to RackLink device: %s", err)
            self._connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from the RackLink device."""
        self._connected = False
        if self._ping_task:
            self._ping_task.cancel()
            try:
                await self._ping_task
            except asyncio.CancelledError:
                pass
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
        self._reader = None
        self._writer = None

    def _escape_data(self, data: list[int]) -> list[int]:
        """Escape protected values in data envelope."""
        escaped: list[int] = []
        protected = [PROTOCOL_HEADER, PROTOCOL_TAIL, PROTOCOL_ESCAPE]
        for byte in data:
            if byte in protected:
                escaped.append(PROTOCOL_ESCAPE)
                escaped.append((~byte) & 0xFF)
            else:
                escaped.append(byte)
        return escaped

    def _unescape_data(self, data: list[int]) -> list[int]:
        """Unescape protected values in data envelope."""
        unescaped: list[int] = []
        i = 0
        while i < len(data):
            if data[i] == PROTOCOL_ESCAPE and i + 1 < len(data):
                unescaped.append((~data[i + 1]) & 0xFF)
                i += 2
            else:
                unescaped.append(data[i])
                i += 1
        return unescaped

    def _calculate_checksum(self, header: int, length: int, data: list[int]) -> int:
        """Calculate 7-bit checksum."""
        total = header + length
        for byte in data:
            total += byte
        return total & 0x7F

    def build_packet(self, data_envelope: list[int]) -> bytes:
        """Build a protocol packet from data envelope."""
        header = PROTOCOL_HEADER
        tail = PROTOCOL_TAIL
        
        # Escape the data envelope
        escaped_envelope = self._escape_data(data_envelope)
        length = len(escaped_envelope)
        
        # Calculate checksum (header + length + unescaped data envelope)
        checksum = self._calculate_checksum(header, length, data_envelope)
        
        # Build packet: header, length, escaped_envelope, checksum, tail
        packet = bytes([header, length] + escaped_envelope + [checksum, tail])
        return packet

    def parse_packet(self, packet: bytes) -> dict[str, Any] | None:
        """Parse a protocol packet."""
        if len(packet) < 5:
            return None
        
        if packet[0] != PROTOCOL_HEADER or packet[-1] != PROTOCOL_TAIL:
            return None
        
        length = packet[1]
        if len(packet) != length + 4:  # header + length + data + checksum + tail
            return None
        
        # Extract escaped envelope and checksum
        escaped_envelope = list(packet[2:-2])
        received_checksum = packet[-2]
        
        # Unescape the envelope
        data_envelope = self._unescape_data(escaped_envelope)
        
        # Verify checksum
        expected_checksum = self._calculate_checksum(PROTOCOL_HEADER, length, data_envelope)
        if received_checksum != expected_checksum:
            _LOGGER.warning("Checksum mismatch: received 0x%02X, expected 0x%02X", 
                          received_checksum, expected_checksum)
            return None
        
        if len(data_envelope) < 3:
            return None
        
        return {
            "destination": data_envelope[0],
            "command": data_envelope[1],
            "subcommand": data_envelope[2],
            "data": data_envelope[3:] if len(data_envelope) > 3 else [],
        }

    async def send_packet(self, packet: bytes) -> None:
        """Send a packet to the device."""
        if not self._connected or not self._writer:
            raise ConnectionError("Not connected to device")
        self._writer.write(packet)
        await self._writer.drain()

    async def receive_packet(self, timeout: float = 5.0) -> dict[str, Any] | None:
        """Receive and parse a packet from the device."""
        if not self._connected or not self._reader:
            raise ConnectionError("Not connected to device")
        
        try:
            # Read header first
            header_bytes = await asyncio.wait_for(self._reader.read(1), timeout=timeout)
            if not header_bytes:
                _LOGGER.debug("No data received (connection closed?)")
                self._connected = False
                return None
                
            if header_bytes[0] != PROTOCOL_HEADER:
                _LOGGER.warning("Invalid header: 0x%02X (expected 0x%02X)", 
                              header_bytes[0], PROTOCOL_HEADER)
                return None
            
            # Read length
            length_bytes = await asyncio.wait_for(self._reader.read(1), timeout=timeout)
            if not length_bytes:
                _LOGGER.debug("No length byte received")
                self._connected = False
                return None
            
            length = length_bytes[0]
            
            if length > 250:  # Max data envelope size per protocol
                _LOGGER.error("Invalid length: %d (max 250)", length)
                return None
            
            # Read rest of packet (data + checksum + tail)
            remaining = await asyncio.wait_for(
                self._reader.read(length + 2), timeout=timeout
            )
            if len(remaining) != length + 2:
                _LOGGER.warning("Incomplete packet: expected %d bytes, got %d", 
                              length + 2, len(remaining))
                self._connected = False
                return None
            
            packet = header_bytes + length_bytes + remaining
            parsed = self.parse_packet(packet)
            
            if parsed:
                _LOGGER.debug("Received packet: cmd=0x%02X, sub=0x%02X", 
                            parsed["command"], parsed["subcommand"])
            
            return parsed
        except asyncio.TimeoutError:
            _LOGGER.debug("Timeout waiting for packet (%.1fs)", timeout)
            return None
        except Exception as e:
            _LOGGER.error("Error receiving packet: %s", e, exc_info=True)
            self._connected = False
            return None

    async def login(self, username: str, password: str) -> bool:
        """Login to the RackLink device.
        
        Per protocol manual: After login, device sends a SET ping message
        that must be responded to with a RESPONSE message.
        """
        login_str = f"{username}|{password}"
        data_envelope = [0x00, CMD_LOGIN, SUB_SET] + list(login_str.encode("ascii"))
        packet = self.build_packet(data_envelope)
        
        _LOGGER.debug("Sending login packet")
        await self.send_packet(packet)
        response = await self.receive_packet(timeout=5.0)
        
        if not response:
            _LOGGER.error("No response to login")
            return False
        
        # Check for NACK
        if response["command"] == CMD_NACK:
            error_code = response["data"][0] if response["data"] else 0
            _LOGGER.error("Login NACK received, error code: 0x%02X", error_code)
            return False
        
        # Check for login response
        if response["command"] == CMD_LOGIN and response["subcommand"] == SUB_RESPONSE:
            if response["data"] and response["data"][0] == 0x01:
                _LOGGER.info("Login successful")
                
                # Per protocol manual: Device sends a SET ping after login
                # We must respond with a RESPONSE
                _LOGGER.debug("Waiting for initial ping from device...")
                ping_response = await self.receive_packet(timeout=5.0)
                
                if ping_response:
                    if ping_response["command"] == CMD_PING and ping_response["subcommand"] == SUB_SET:
                        _LOGGER.debug("Received initial ping, responding...")
                        # Respond with pong
                        pong_envelope = [0x00, CMD_PING, SUB_RESPONSE]
                        pong_packet = self.build_packet(pong_envelope)
                        await self.send_packet(pong_packet)
                        _LOGGER.debug("Sent pong response")
                        return True
                    else:
                        _LOGGER.warning("Expected ping after login, got command 0x%02X", 
                                      ping_response["command"])
                        # Still consider login successful if we got login response
                        return True
                else:
                    _LOGGER.warning("No ping received after login, but login was successful")
                    return True
        
        _LOGGER.error("Login failed - unexpected response: command=0x%02X, sub=0x%02X",
                     response["command"], response["subcommand"])
        return False

    async def ping(self) -> bool:
        """Send ping and wait for pong.
        
        Note: Some devices may not respond to client-initiated pings.
        The protocol manual states devices send pings that we must respond to.
        """
        data_envelope = [0x00, CMD_PING, SUB_SET]
        packet = self.build_packet(data_envelope)
        
        _LOGGER.debug("Sending ping...")
        await self.send_packet(packet)
        response = await self.receive_packet(timeout=3.0)
        
        if response:
            _LOGGER.debug("Ping response: cmd=0x%02X, sub=0x%02X", 
                         response["command"], response["subcommand"])
            if response["command"] == CMD_PING and response["subcommand"] == SUB_RESPONSE:
                _LOGGER.debug("Ping successful")
                return True
            elif response["command"] == CMD_NACK:
                error_code = response["data"][0] if response["data"] else 0
                _LOGGER.debug("Ping received NACK, error: 0x%02X", error_code)
        else:
            _LOGGER.debug("No response to ping (device may not support client-initiated pings)")
        
        return False

    async def send_command(
        self, command: int, subcommand: int, data: list[int] | None = None
    ) -> dict[str, Any] | None:
        """Send a command and return the response."""
        data_envelope = [0x00, command, subcommand]
        if data:
            data_envelope.extend(data)
        
        packet = self.build_packet(data_envelope)
        await self.send_packet(packet)
        
        response = await self.receive_packet(timeout=5.0)
        
        # Check for NACK
        if response and response["command"] == CMD_NACK:
            error_code = response["data"][0] if response["data"] else 0
            _LOGGER.warning("Command 0x%02X received NACK, error code: 0x%02X", 
                          command, error_code)
            return None
        
        return response

    async def get_outlet_count(self) -> int | None:
        """Get the number of power outlets."""
        response = await self.send_command(CMD_OUTLET_COUNT, SUB_GET)
        if response and response["command"] == CMD_OUTLET_COUNT and response["subcommand"] == SUB_RESPONSE:
            if response["data"]:
                return response["data"][0]
        return None

    async def get_outlet_state(self, outlet_index: int) -> bool | None:
        """Get the state of a power outlet (1-indexed)."""
        response = await self.send_command(CMD_POWER_OUTLETS, SUB_GET, [outlet_index])
        if response and response["command"] == CMD_POWER_OUTLETS and response["subcommand"] == SUB_RESPONSE:
            if len(response["data"]) >= 2:
                return response["data"][1] == 0x01  # 0x01 = ON
        return None

    async def set_outlet_state(self, outlet_index: int, state: bool) -> bool:
        """Set the state of a power outlet (1-indexed)."""
        state_byte = 0x01 if state else 0x00
        response = await self.send_command(CMD_POWER_OUTLETS, SUB_SET, [outlet_index, state_byte])
        if response and response["command"] == CMD_POWER_OUTLETS and response["subcommand"] == SUB_RESPONSE:
            return True
        return False

    async def get_outlet_name(self, outlet_index: int) -> str | None:
        """Get the name of a power outlet."""
        response = await self.send_command(CMD_OUTLET_NAME, SUB_GET, [outlet_index])
        if response and response["command"] == CMD_OUTLET_NAME and response["subcommand"] == SUB_RESPONSE:
            if len(response["data"]) > 1:
                name_bytes = response["data"][1:]
                return bytes(name_bytes).decode("ascii", errors="ignore").rstrip("\x00")
        return None
