# Backup security notes — 2026-09-06

## Do not publish

The raw server archives contain data that should not be committed to a public repository:

- HBLink master/OpenBridge passphrases
- HBMonitor web password values
- downloaded RadioID subscriber/repeater databases
- runtime logs
- any future private keys, tokens or credentials

## Public repository policy

Use sanitized configuration examples with credentials replaced by `<REDACTED>` or environment/secret references.

Keep the original server archives in a private/offline disaster-recovery location.

## Current live configuration observation

HBMonitor's supplied configuration has `WEB_AUTH = False`. If the dashboard is exposed beyond a trusted network, authentication and network access controls should be reviewed before making the service publicly reachable.

## Recovery principle

A restore should be performed from a known-good sanitized source tree plus a separately protected secret/configuration package. Never copy credentials from public Git history.
