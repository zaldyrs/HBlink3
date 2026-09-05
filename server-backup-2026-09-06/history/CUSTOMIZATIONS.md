# Live-server customization notes

Collected from `/opt/hblink3` on 2026-09-06.

## 1. HBMonitor Last Heard integration

The live `hblink.py` contains custom logic in `OPENBRIDGE.dmrd_received()` that:

- Handles group calls when reporting is enabled.
- Tracks one active transmission per DMR stream ID.
- Sends a `GROUP VOICE,START,RX,...` reporting event when a stream starts.
- Detects `dtype/vseq == 2` as the voice terminator.
- Calculates transmission duration.
- Sends a `GROUP VOICE,END,RX,...,<duration>` reporting event.
- Logs START and END events for troubleshooting.
- Wraps reporting calls in exception handling so a reporting failure does not directly crash the call-processing path.

## 2. Reporting client fix

The live `hblink.py` changed the reporting client's CONFIG request handling from calling `self.send_config()` to calling `self._factory.send_config()`.

This addresses the reporting protocol object versus factory ownership of `send_config()`.

## 3. Configuration

Live configuration has:

- HBLink master enabled.
- UDP master port 62035.
- Maximum 10 peers.
- Reporting enabled every 60 seconds.
- Reporting TCP port 4321.
- Reporting client restricted to localhost.
- ACL processing enabled, with the current ACLs configured to permit all.
- RadioID alias downloading disabled.

## 4. Historical source variants

The live server contained multiple historical copies of `hblink.py` and `bridge.py`, including files named `*.bak`, `*.backup`, `*.before-*`, and `*.final-backup`.

These are useful for reconstructing the evolution of the fixes. The raw archive preserves them; the public repository should keep secrets out of those historical configuration copies.

## 5. HBMonitor dependency

HBLink3 reporting is coupled to the separately installed HBMonitor service at `/opt/hbmonitor-src/HBmonitor`.

The HBMonitor source itself was not included in the uploaded HBLink3 archive, so it should be backed up separately before making major changes to the reporting protocol.
