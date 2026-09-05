# Live HBLink3 + HBMonitor architecture — 2026-09-06

## Runtime topology

```text
DMR peers/repeaters
        |
        | Homebrew Repeater Protocol / UDP
        v
+-------------------------+
| HBLink3                 |
| /opt/hblink3            |
| hblink.py               |
| systemd: hblink3.service|
+------------+------------+
             |
             | TCP reporting :4321
             v
+--------------------------+
| HBMonitor                |
| /opt/hbmonitor-src/...   |
| monitor.py               |
| systemd: hbmonitor.service|
+------------+-------------+
             |
       +-----+------+
       |            |
       v            v
    HTTP :8080   WebSocket :9000
       |
       v
   Web dashboard
```

## HBLink3

- Working directory: `/opt/hblink3`
- Python: `/opt/hblink3/venv/bin/python`
- Entry point: `hblink.py`
- systemd unit: `/etc/systemd/system/hblink3.service`
- Master UDP port: `62035`
- Reporting TCP port: `4321`
- Reporting client on the live configuration: `127.0.0.1`

## HBMonitor

- Working directory: `/opt/hbmonitor-src/HBmonitor`
- Python: `/opt/hbmonitor-src/HBmonitor/venv/bin/python`
- Entry point: `monitor.py`
- systemd unit: `/etc/systemd/system/hbmonitor.service`
- Web server: `8080`
- WebSocket: `9000`
- HBLink reporting endpoint: `127.0.0.1:4321`

## Data flow

1. HBLink receives DMR traffic from connected peers.
2. HBLink's reporting server periodically publishes configuration/status data.
3. The custom DMR receive path generates Last Heard START/END bridge events.
4. HBMonitor receives reporting/configuration data and bridge events.
5. HBMonitor updates repeater/peer tables and Last Heard data.
6. The web UI presents repeater status, map/location information and Last Heard information.

## Security boundary

The reporting socket is configured for localhost in the live HBMonitor configuration. The HBLink master UDP service is externally reachable on its configured port. Dashboard authentication is currently disabled in the supplied HBMonitor configuration, so the web exposure should be reviewed before publishing the dashboard to an untrusted network.

## Backup boundary

The disaster-recovery archive is separate from the public GitHub source repository. Runtime virtual environments, downloaded RadioID databases and logs should not be committed to source control. Secret-bearing configuration must remain private.
