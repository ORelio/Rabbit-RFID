#!/usr/bin/env python3

# ===================================================================================
# nabstate - remotely monitor and change the sleep/awake state (Nabaztag/tag:tag:tag)
# Monitoring state works using nabd, changing state is done using nabweb
# By ORelio (c) 2023-2024 - CDDL 1.0
# ===================================================================================

from threading import Lock
from typing import Callable

import rabbits
import nabweb
import nabd

from events import EventHandler
from logs import logs

_state_lock = Lock()
_stateinfo = dict()
_sleeping = dict()

STATE_IDLE = 'idle'
STATE_ASLEEP = 'asleep'
STATE_FALLING_ASLEEP = 'falling_asleep'
STATE_WAKING_UP = 'waking_up'
STATE_OFFLINE = 'offline'

'''
Nabstate Event Handler
Callbacks will receive args = rabbit: str,  new_state: str
'''
event_handler = EventHandler('Nabstate', log_level=None)

def get_state(rabbit: str):
    '''
    Get current Nabaztag state
    '''
    nabaztag_ip = rabbits.get_ip(rabbit)
    with _state_lock:
        return _stateinfo.get(nabaztag_ip, STATE_OFFLINE)

def _nabd_state_monitor(rabbit: str, nabd_event: dict):
    '''
    Internal. Callback for monitoring nabd events
    '''
    nabaztag_ip = rabbits.get_ip(rabbit)
    if 'type' in nabd_event and nabd_event['type'] == 'state' and 'state' in nabd_event:
        _cache_current_state(nabaztag_ip, nabd_event['state'])
        _handle_sleep_wakeup_event(nabaztag_ip, nabd_event['state'])
        event_handler.dispatch(rabbits.get_name(nabaztag_ip), nabd_event['state'])

def _cache_current_state(rabbit: str, state: str):
    '''
    Internal. Take note of new Nabaztag state
    '''
    nabaztag_ip = rabbits.get_ip(rabbit)
    with _state_lock:
        _stateinfo[nabaztag_ip] = state

def _handle_sleep_wakeup_event(rabbit: str, state: str):
    '''
    Internal. Detect transition between sleep <=> awake state and generate a specific event
    '''
    nabaztag_ip = rabbits.get_ip(rabbit)
    logs.info('New state for ' + rabbits.get_name(rabbit) + ': ' + state)
    if state == STATE_ASLEEP or state == STATE_IDLE:
        new_sleep_state = (state == STATE_ASLEEP)
        old_sleep_state = new_sleep_state
        with _state_lock:
            if nabaztag_ip in _sleeping:
                old_sleep_state = _sleeping[nabaztag_ip]
            _sleeping[nabaztag_ip] = new_sleep_state
        if new_sleep_state != old_sleep_state:
            event = STATE_FALLING_ASLEEP if new_sleep_state else STATE_WAKING_UP
            event_handler.dispatch(rabbits.get_name(nabaztag_ip), event)

def initialize(rabbit: str):
    '''
    Start monitoring Nabaztag state in a background thread
    '''
    nabaztag_ip = rabbits.get_ip(rabbit)
    nabd.event_handler.subscribe(_nabd_state_monitor)
    nabd.connect(nabaztag_ip)

def set_sleeping(rabbit: str, sleeping: bool, play_sound: bool = False):
    '''
    Set Nabaztag sleeping state
    '''
    nabaztag_ip = rabbits.get_ip(rabbit)

    # Adjust settings
    nabweb.change_settings(nabaztag_ip, nabweb.API_NABCLOCKD, {
        'play_wakeup_sleep_sounds': str(play_sound).lower(),
        'settings_per_day': 'false',
    })

    # Change state only if current state is not the desired state
    current_state = get_state(nabaztag_ip)
    if current_state == STATE_OFFLINE:
        return # Cannot change state
    if current_state == STATE_ASLEEP and sleeping:
        return # Already sleeping
    if current_state != STATE_ASLEEP and not sleeping:
        return # Already awake (idle or doing something else)

    # Change setting to cancel manual wakeup - pressing nabaztag button to wake it up
    nabweb.change_settings(nabaztag_ip, nabweb.API_NABCLOCKD, {
        'sleep_time': '00:00',
        'wakeup_time': '00:00',
    })

    # Set sleep time so that nabaztag will be always awake or always sleeping
    nabweb.change_settings(nabaztag_ip, nabweb.API_NABCLOCKD, {
        'sleep_time': '00:00' if sleeping else '99:99',
        'wakeup_time': '99:99' if sleeping else '00:00',
    })

    # The sleep_wakeup_event will occur after a delay (a few seconds)
    # If we successfully woke up a rabbit, we want to make it appear awake
    # immediately as some scenarios will not occur if is_sleeping() returns True
    if not sleeping:
        _cache_current_state(rabbit, STATE_IDLE)

def any_sleeping() -> bool:
    '''
    Check if at least one rabbit is currently asleep
    '''
    for rabbit in rabbits.get_all():
        if get_state(rabbit) == STATE_ASLEEP or get_state(rabbit) == STATE_OFFLINE:
            return True
    return False

def is_sleeping(rabbit: str) -> bool:
    '''
    Check if the specified rabbit is currently sleeping
    '''
    return get_state(rabbit) == STATE_ASLEEP or get_state(rabbit) == STATE_OFFLINE

# Initialize nabstate on first module import
for rabbit in rabbits.get_all():
    logs.debug('Initializing: ' + rabbit)
    initialize(rabbit)
