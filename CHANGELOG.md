# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
