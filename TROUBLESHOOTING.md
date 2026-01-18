# Troubleshooting Guide

## Connection Issues

### "Ping failed, reconnecting..." Errors

If you see repeated "Ping failed, reconnecting..." messages in your logs:

**Cause**: The RLNK-SW715R device does not respond to client-initiated ping commands. This is normal behavior - the device sends pings that we respond to, but doesn't respond to pings we send.

**Solution**: 
1. **Restart Home Assistant** to load the updated code that handles this correctly
2. The integration will now use actual commands (like outlet count) to test the connection instead of ping
3. Ping failures are now non-fatal and won't cause reconnection attempts

### "Connection refused" Errors

If you see `[Errno 111] Connect call failed` errors:

**Possible causes**:
1. Device is offline or unreachable
2. Firewall blocking port 60000
3. Device IP address changed
4. Control protocol not enabled on device

**Solutions**:
1. Verify device is online: `ping 192.168.1.252` (replace with your device IP)
2. Check port 60000 is accessible: `telnet 192.168.1.252 60000`
3. Verify IP address in integration settings
4. For Premium+ models: Ensure control protocol is enabled in Device Settings → Network Services → Control Protocol
5. For Select/Premium: Ensure you've logged into the web interface at least once to enable the protocol

### Connection Drops After Successful Login

If connection succeeds but then immediately drops:

**Cause**: Device may be closing idle connections, or there's a network issue.

**Solution**:
1. The integration now uses outlet commands to test connection instead of ping
2. Connection state is better tracked
3. Automatic reconnection on command failures

## After Updating Code

**Important**: After updating the integration code, you **must restart Home Assistant** for changes to take effect.

1. Go to **Settings** → **System** → **Hardware**
2. Click the three dots (⋮) → **Restart**
3. Or use the restart button in Developer Tools

## Log Analysis

### Normal Operation
```
INFO: Connected to RackLink device at 192.168.1.252:60000
INFO: Login successful
DEBUG: Ping not supported (normal for RLNK-SW715R), testing with command
```

### Connection Issues
```
ERROR: Failed to connect to RackLink device: [Errno 111] Connect call failed
```
→ Check device accessibility and network

### Authentication Issues
```
ERROR: Login failed
```
→ Verify username and password are correct

## Testing Connection

Use the standalone diagnostic tool to test your device:

```bash
python3 standalone/diagnose.py 192.168.1.252 -P your_password
```

This will help identify specific connection issues.

## Device-Specific Notes

### RLNK-SW715R
- Does not respond to client-initiated pings (this is normal)
- Uses TCP port 60000
- Default username: "user"
- Control protocol enabled by default after first web login

### Premium+ Models
- Control protocol must be manually enabled
- Can use any admin account with control protocol enabled
- No default "user" account

## Enabling Debug Logging

To see detailed debug information, add this to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.racklink: debug
```

Then restart Home Assistant. You'll see detailed logs for:
- Connection attempts and status
- All commands sent and responses received
- Packet building and parsing
- Sensor value reading and parsing
- Outlet state fetching
- Error details with stack traces

## Getting Help

If issues persist:
1. Check Home Assistant logs: **Settings** → **System** → **Logs**
2. Enable debug logging (see above)
3. Run the diagnostic tool and share the output
4. Open an issue on GitHub with:
   - Device model
   - Home Assistant version
   - Integration version
   - Relevant log excerpts (with debug logging enabled)
   - Diagnostic tool output
