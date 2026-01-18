# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-12-XX

### Added
- Sensor monitoring: Temperature, Voltage, Current, Power, Power Factor, Thermal Load, Occupancy
- Full sensor entity support with proper device classes and units
- Improved connection state management

### Changed
- Removed ping requirement (not necessary for RLNK-SW715R)
- Connection testing now uses actual commands instead of ping
- Better error handling for individual outlet and sensor failures

### Fixed
- Connection stability issues
- Unnecessary reconnection attempts on ping failures

## [1.0.0] - 2024-12-XX

### Added
- Initial release of RackLink Home Assistant integration
- Support for RLNK-SW715R and compatible RackLink devices
- Power outlet control (on/off)
- Outlet state monitoring
- Automatic outlet discovery
- Connection status sensor
- Config flow for easy setup
- Automatic reconnection handling
- Full protocol implementation (I-00472 Series Protocol Manual)
- Standalone CLI tool for testing
- Protocol explorer web application

### Features
- TCP/IP communication on port 60000
- Login authentication
- Ping/Pong keepalive (device-initiated)
- Outlet count detection
- Outlet name retrieval
- Outlet state reading and control
- Robust error handling and reconnection
