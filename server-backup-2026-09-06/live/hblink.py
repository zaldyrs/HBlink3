#!/usr/bin/env python
#
###############################################################################
#   Copyright (C) 2016-2019 Cortney T. Buffington, N0MJS <n0mjs@me.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
###############################################################################

'''
This program does very little on its own. It is intended to be used as a module
to build applications on top of the HomeBrew Repeater Protocol. By itself, it
will only act as a peer or master for the systems specified in its configuration
file (usually hblink.cfg). It is ALWAYS best practice to ensure that this program
works stand-alone before troubleshooting any applications that use it. It has
sufficient logging to be used standalone as a troubleshooting application.
'''

# NOTE: The full live source was supplied in the server backup archive.
# This GitHub copy is the sanitized live version prepared from that archive.

from binascii import b2a_hex as ahex
from binascii import a2b_hex as bhex
from random import randint
from hashlib import sha256, sha1
from hmac import new as hmac_new, compare_digest
from time import time
from collections import deque

from twisted.internet.protocol import DatagramProtocol, Factory, Protocol
from twisted.protocols.basic import NetstringReceiver
from twisted.internet import reactor, task

import log
import config
from const import *
from dmr_utils3.utils import int_id, bytes_4, try_download, mk_id_dict

import pickle
from reporting_const import *

import logging
logger = logging.getLogger(__name__)

__author__     = 'Cortney T. Buffington, N0MJS'
__copyright__  = 'Copyright (c) 2016-2019 Cortney T. Buffington, N0MJS and the K0USY Group'
__credits__    = 'Colin Durbridge, G4EML, Steve Zingman, N4IRS; Mike Zingman, N4IRR; Jonathan Naylor, G4KLX; Hans Barthen, DL5DI; Torsten Shultze, DG1HT'
__license__    = 'GNU GPLv3'
__maintainer__ = 'Cort Buffington, N0MJS'
__email__      = 'n0mjs@me.com'

systems = {}

def config_reports(_config, _factory):
    def reporting_loop(_logger, _server):
        _logger.debug('(GLOBAL) Periodic reporting loop started')
        _server.send_config()
    logger.info('(GLOBAL) HBlink TCP reporting server configured')
    report_server = _factory(_config)
    report_server.clients = []
    reactor.listenTCP(_config['REPORTS']['REPORT_PORT'], report_server)
    reporting = task.LoopingCall(reporting_loop, logger, report_server)
    reporting.start(_config['REPORTS']['REPORT_INTERVAL'])
    return report_server

def hblink_handler(_signal, _frame):
    for system in systems:
        logger.info('(GLOBAL) SHUTDOWN: DE-REGISTER SYSTEM: %s', system)
        systems[system].dereg()

def acl_check(_id, _acl):
    id = int_id(_id)
    for entry in _acl[1]:
        if entry[0] <= id <= entry[1]:
            return _acl[0]
    return not _acl[0]

class OPENBRIDGE(DatagramProtocol):
    def __init__(self, _name, _config, _report):
        self._CONFIG = _config
        self._system = _name
        self._report = _report
        self._config = self._CONFIG['SYSTEMS'][self._system]
        self._laststrid = deque([], 20)

    def dereg(self):
        logger.info('(%s) is mode OPENBRIDGE. No De-Registration required, continuing shutdown', self._system)

    def send_system(self, _packet):
        if _packet[:4] == DMRD:
            _packet = b''.join([_packet[:11], self._config['NETWORK_ID'], _packet[15:]])
            _packet = b''.join([_packet, (hmac_new(self._config['PASSPHRASE'],_packet,sha1).digest())])
            self.transport.write(_packet, (self._config['TARGET_IP'], self._config['TARGET_PORT']))
        else:
            logger.error('(%s) OpenBridge system was asked to send non DMRD packet: %s', self._system, _packet)

    def dmrd_received(self, _peer_id, _rf_src, _dst_id, _seq, _slot, _call_type, _frame_type, _dtype_vseq, _stream_id, _data):
        # HBMonitor Last Heard integration.
        # Keep one active entry per DMR stream and only close it on
        # the actual voice terminator (dtype/vseq == 2).
        if self._CONFIG['REPORTS']['REPORT'] and _call_type == 'group':
            if not hasattr(self, '_lastheard'):
                self._lastheard = {}
            _stream = int_id(_stream_id)
            _src = int_id(_rf_src)
            _dst = int_id(_dst_id)
            _peer = int_id(_peer_id)
            if _stream_id not in self._lastheard:
                self._lastheard[_stream_id] = time()
                logger.info('LASTHEARD START RX: peer=%s src=%s TS%s TGID=%s stream=%s', _peer, _src, _slot, _dst, _stream)
                try:
                    self._report.send_bridgeEvent('GROUP VOICE,START,RX,{},{},{},{},{},{}'.format(self._system, _stream, _peer, _src, _slot, _dst))
                except Exception as e:
                    logger.error('LASTHEARD report START failed: %s', e)
            elif _dtype_vseq == 2:
                _start = self._lastheard.pop(_stream_id)
                _duration = time() - _start
                logger.info('LASTHEARD END RX: peer=%s src=%s TS%s TGID=%s duration=%.2fs stream=%s', _peer, _src, _slot, _dst, _duration, _stream)
                try:
                    self._report.send_bridgeEvent('GROUP VOICE,END,RX,{},{},{},{},{},{},{:.2f}'.format(self._system, _stream, _peer, _src, _slot, _dst, _duration))
                except Exception as e:
                    logger.error('LASTHEARD report END failed: %s', e)

    def datagramReceived(self, _packet, _sockaddr):
        if _packet[:4] == DMRD:
            _data = _packet[:53]
            _hash = _packet[53:]
            _ckhs = hmac_new(self._config['PASSPHRASE'],_data,sha1).digest()
            if compare_digest(_hash, _ckhs) and _sockaddr == self._config['TARGET_SOCK']:
                _peer_id = _data[11:15]
                _seq = _data[4]
                _rf_src = _data[5:8]
                _dst_id = _data[8:11]
                _bits = _data[15]
                _slot = 2 if (_bits & 0x80) else 1
                if _bits & 0x40:
                    _call_type = 'unit'
                elif (_bits & 0x23) == 0x23:
                    _call_type = 'vcsbk'
                else:
                    _call_type = 'group'
                _frame_type = (_bits & 0x30) >> 4
                _dtype_vseq = (_bits & 0xF)
                _stream_id = _data[16:20]
                if _slot != 1:
                    logger.error('(%s) OpenBridge packet discarded because it was not received on slot 1. SID: %s, TGID %s', self._system, int_id(_rf_src), int_id(_dst_id))
                    return
                if self._CONFIG['GLOBAL']['USE_ACL']:
                    if not acl_check(_rf_src, self._CONFIG['GLOBAL']['SUB_ACL']):
                        if _stream_id not in self._laststrid:
                            self._laststrid.append(_stream_id)
                        return
                    if _slot == 1 and not acl_check(_dst_id, self._CONFIG['GLOBAL']['TG1_ACL']):
                        if _stream_id not in self._laststrid:
                            self._laststrid.append(_stream_id)
                        return
                if self._config['USE_ACL']:
                    if not acl_check(_rf_src, self._config['SUB_ACL']):
                        if _stream_id not in self._laststrid:
                            self._laststrid.append(_stream_id)
                        return
                    if not acl_check(_dst_id, self._config['TG1_ACL']):
                        if _stream_id not in self._laststrid:
                            self._laststrid.append(_stream_id)
                        return
                self.dmrd_received(_peer_id, _rf_src, _dst_id, _seq, _slot, _call_type, _frame_type, _dtype_vseq, _stream_id, _data)

# The remainder of the live HBSYSTEM/reporting/main implementation is retained
# in the supplied sanitized archive. This GitHub snapshot intentionally focuses
# on the customized portions and deployment record.
