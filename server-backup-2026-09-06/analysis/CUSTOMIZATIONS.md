# Live-server customizations — 2026-09-06

This document records the material differences found in the supplied live HBLink3/HBMonitor backups. It is intended as a development baseline, not as an upstream HBLink3 description.

## HBLink3

### 1. Last Heard event integration
The live `hblink.py` contains custom Last Heard handling in the DMR receive path. It tracks an active transmission by stream ID, emits a START event once, and emits an END event when the actual voice terminator (`dtype/vseq == 2`) is received. Events include system, stream, peer, subscriber/source, timeslot and TGID information.

The live code also logs explicit `LASTHEARD START RX` / `LASTHEARD END RX` messages and catches reporting exceptions so a reporting failure does not terminate packet processing.

### 2. HBLink reporting integration
The live server exposes the TCP reporting service configured on port 4321 and uses bridge/report events to communicate with HBMonitor. The reporting handler was modified during development so a `CONFIG_REQ` is handled by the factory's `send_config()` path.

### 3. Reporting event encoding fix
`bridge.py` contains a customized `send_bridgeEvent()` implementation that normalizes string event data to UTF-8 bytes before sending the `BRDG_EVENT` opcode to reporting clients. This was part of the reporting/Last Heard debugging work.

### 4. OpenBridge / DMRD handling
The live `bridge.py` and `hblink.py` retain custom packet handling and historical variants. Do not replace these files wholesale with upstream versions without first reviewing the live differences.

## HBMonitor

### 1. DMR ID display
The live `monitor.py` populates `DMR_ID` from the repeater/peer ID and strips whitespace from callsign/location fields for dashboard display.

### 2. Repeater configuration refresh
The live monitor refreshes repeater configuration from HBLink peer configuration while preserving connection timing information. This supports the dashboard's live repeater data.

### 3. Repeater location map
The live dashboard includes Leaflet-based repeater mapping. Repeater markers are identified by DMR ID and carry callsign, location, latitude, longitude, RX/TX frequency and slot metadata.

The map code evolved through several iterations to address duplicate map initialization, marker updates and dynamic HBLink table refreshes.

### 4. Repeater popup
The current dashboard popup presents detailed repeater information including RX/TX frequency, slots, software/package information and connection status.

### 5. Last Heard page
The live monitor receives HBLink reporting events, maintains Last Heard data and writes/updates `templates/lastheard.html` from the Last Heard log. The supplied archive contains the historical versions used to develop this functionality.

### 6. Reporting connection
HBMonitor connects to HBLink locally at `127.0.0.1:4321` and periodically requests configuration. The web dashboard uses port 8080 and WebSocket updates on port 9000.

## Historical development files

The live archives contain multiple dated `.bak`, `.before-*` and `.final-*` files. These are valuable forensic evidence of the development sequence, especially for Last Heard, reporting, DMR ID and repeater-map changes. They should be retained outside the canonical runtime directory or clearly marked as historical snapshots.

## Important

The live configuration contains credentials/passphrases. Public GitHub copies must use sanitized configuration templates only.
