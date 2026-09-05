# Live patch details

These are the material custom changes identified by comparing the supplied live server files with the historical copies present on the same server.

## `hblink.py`

### Last Heard reporting

In `OPENBRIDGE.dmrd_received()`, the live server adds stream tracking and HBMonitor events:

```python
if self._CONFIG['REPORTS']['REPORT'] and _call_type == 'group':
    if not hasattr(self, '_lastheard'):
        self._lastheard = {}

    _stream = int_id(_stream_id)
    _src = int_id(_rf_src)
    _dst = int_id(_dst_id)
    _peer = int_id(_peer_id)

    if _stream_id not in self._lastheard:
        self._lastheard[_stream_id] = time()
        self._report.send_bridgeEvent(
            'GROUP VOICE,START,RX,{},{},{},{},{},{}'.format(
                self._system, _stream, _peer, _src, _slot, _dst
            )
        )
    elif _dtype_vseq == 2:
        _start = self._lastheard.pop(_stream_id)
        _duration = time() - _start
        self._report.send_bridgeEvent(
            'GROUP VOICE,END,RX,{},{},{},{},{},{},{:.2f}'.format(
                self._system, _stream, _peer, _src, _slot, _dst, _duration
            )
        )
```

The live implementation also logs START/END events and catches exceptions around the reporting calls.

### Reporting CONFIG request fix

The live `report.process_message()` uses:

```python
self._factory.send_config()
```

instead of calling `self.send_config()` on the protocol object.

## `bridge.py`

The live `bridgeReportFactory.send_bridgeEvent()` accepts string data, encodes it as UTF-8, logs the outgoing event, and catches failures from `send_clients()`:

```python
if isinstance(_data, str):
    _data = _data.encode('utf-8', errors='ignore')
logger.warning("(REPORT) BRIDGE EVENT: %r", _data)
try:
    self.send_clients(REPORT_OPCODES['BRDG_EVENT'] + _data)
except Exception as e:
    logger.exception("(REPORT) send_clients FAILED: %s", e)
```

## Historical evidence

The supplied archive contains multiple dated/labelled source backups showing the evolution of these changes. The canonical live source remains in the original local archive; this document records the important deltas so future development can reproduce and review them.
