# HACS Setup Guide

This repository is configured for installation via HACS (Home Assistant Community Store).

## Repository Structure

The repository is organized as follows:

```
Racklink-2-HomeAssistant/
├── custom_components/
│   └── racklink/          # Integration files (HACS will install this)
│       ├── __init__.py
│       ├── config_flow.py
│       ├── coordinator.py
│       ├── protocol.py
│       ├── switch.py
│       ├── sensor.py
│       ├── const.py
│       ├── manifest.json
│       └── README.md
├── hacs.json              # HACS configuration
├── info.md                # HACS display information
├── .hacsignore            # Files to ignore during HACS install
├── CHANGELOG.md           # Version history
└── README.md              # Main documentation
```

## HACS Configuration

### hacs.json
- Defines the integration category
- Sets minimum Home Assistant version
- Enables README rendering

### info.md
- Displayed in HACS when viewing the integration
- Contains installation and usage instructions
- Shown to users before installation

### .hacsignore
- Excludes non-integration files from HACS installation
- Prevents Node.js files, PDFs, and other dev files from being installed
- Only installs the `custom_components/racklink/` directory

## Adding to HACS

### For Users:

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the three dots (⋮) → **Custom repositories**
4. Add repository:
   - URL: `https://github.com/whatcheer/Racklink-2-HomeAssistant`
   - Category: **Integration**
5. Search for "RackLink" and install

### For Repository Owners:

1. Ensure all files are committed to the repository
2. Create a release tag (e.g., `v1.0.0`) for version tracking
3. HACS will automatically detect new versions from tags

## Version Management

- Update version in `custom_components/racklink/manifest.json`
- Update `CHANGELOG.md` with changes
- Create a git tag: `git tag v1.0.0`
- Push tag: `git push origin v1.0.0`

## Validation

The repository includes GitHub Actions workflows:
- `validate.yml` - Validates integration structure
- `hacs.yml` - HACS-specific validation

These run automatically on push/PR to ensure compatibility.

## Testing HACS Installation

Before publishing:
1. Test installation via HACS custom repository
2. Verify all files are included correctly
3. Check that excluded files are not installed
4. Test integration functionality

## Notes

- The `standalone/` directory is excluded (CLI tools)
- The `components/` directory is excluded (React web app)
- Protocol PDF is excluded
- Only integration files in `custom_components/racklink/` are installed
