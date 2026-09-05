# HBLink3 Live Server Backup — 2026-09-06

This directory is a sanitized snapshot of the live `/opt/hblink3` installation collected on 2026-09-06.

## Contents
- `live/` — canonical live HBLink3 source files from the server
- `config/` — sanitized live and historical configuration files
- `systemd/` — service unit files for HBLink3 and HBMonitor
- `history/` — checksums and notes about historical backup variants

## Server baseline
- Hostname: `hblink.mim.id`
- OS: Ubuntu 24.04.4 LTS
- Kernel: 6.8.0-138-generic
- Architecture: x86-64
- Virtualization: KVM
- Python: 3.12.3
- HBLink3 path: `/opt/hblink3`
- HBLink3 service: `hblink3.service`
- HBMonitor path: `/opt/hbmonitor-src/HBmonitor`
- HBMonitor service: `hbmonitor.service`

## Important security note
The raw server archive contained a real HBLink configuration secret. It is intentionally NOT committed to this public repository. All committed configuration copies replace `PASSPHRASE` values with `<REDACTED>`.

Keep the original `hblink3-source-backup.tar.gz` as a private/offline backup only.

## Live customization identified
The live `hblink.py` contains custom HBMonitor Last Heard reporting logic in `OPENBRIDGE.dmrd_received()`, including START/END events and stream-duration tracking. The live source also contains a reporting-client fix using `self._factory.send_config()`.

The live `bridge.py` contains reporting event handling around `send_bridgeEvent()`.

The historical `.bak` files are retained in the original local archive for forensic/change-history purposes, but are not all duplicated in GitHub.
