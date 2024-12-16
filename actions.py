#!/usr/bin/env python3

# ===============================================================
# action - map config entries to actions for use by other modules
# By ORelio (c) 2024 - CDDL 1.0
# ===============================================================

import json
import requests

from logs import logs

import nabstate
import nabweb

def str2action(action: str, setting_name: str = None) -> 'Action':
    '''
    Convert setting (str) to action (object)
    type:name[:data] => object representation
    raises ValueError for invalid syntax or unavailable action type

    Supported actions:
     webhook:url <- example: http://example.com/?mywebhook
     weather[:rabbit_name]
     airquality[:rabbit_name]
     taichi[:rabbit_name]

    Notes:
     [text in brackets] means optional part in action data
     omitting rabbit_name is possible for rabbit-related events such as rfid
    '''
    if not setting_name:
        setting_name = '<unknown setting>'

    action_fields = action.split(':')
    if len(action_fields) < 1:
        raise ValueError('Invalid action format for "{}", expecting {}, got "{}"'.format(
            setting_name, 'type:[name[:data]]', action))

    action_type = action_fields[0].lower()
    action_name = action_fields[1] if len(action_fields) > 1 else None
    action_name_and_data = action[len(action_type) + 1:] if len(action_fields) > 1 else None

    if action_type == 'webhook':
        return WebhookAction(action_name_and_data, None)
    elif action_type == 'sleep':
        return SleepAction(action_name, None)
    elif action_type == 'weather':
        return WeatherAction(action_name, None)
    elif action_type == 'airquality':
        return AirQualityAction(action_name, None)
    elif action_type == 'taichi':
        return TaichiAction(action_name, None)
    else:
        raise ValueError('Unknown action type for "{}", expecting {}, got "{}"'.format(
        setting_name, 'webhook|sleep|weather|airquality|taichi', action_type))

class Action:
    '''
    Represents a generic action having a run() function
    rabbit is used for rabbit-related actions, ignored otherwise.
    '''
    def __init__(self, name: str, data: str = None):
        raise NotImplementedError('__init__ not implemented.')
    def run(self, rabbit = None):
        raise NotImplementedError('run() not implemented.')
    def __repr__(self):
        raise NotImplementedError('__repr__ not implemented.')

class WebhookAction(Action):
    '''
    Call the specified URL (HTTP GET)
    '''
    def __init__(self, name: str, data: str = None):
        self.url = name
    def run(self, rabbit = None):
        try:
            requests.get(self.url, timeout=30).raise_for_status()
            logs.info('Called webhook URL: {}'.format(self.url))
        except:
            logs.error('Failed to call webhook URL: {}'.format(self.url))
    def __repr__(self):
        return 'WebhookAction({})'.format(self.url)

class SleepAction(Action):
    '''
    Put a rabbit to sleep by overriding its sleep hours settings
    '''
    default_rabbit = None
    def __init__(self, name: str, data: str = None):
        self.default_rabbit = name
    def run(self, event_type = None, rabbit = None, secondary_action: bool = False):
        if (rabbit or self.default_rabbit) and not secondary_action:
            nabstate.set_sleeping(rabbit if rabbit else self.default_rabbit, sleeping=True, play_sound=True)
    def __repr__(self):
        return 'SleepAction({})'.format(self.default_rabbit)

class WeatherAction(Action):
    '''
    Launch Weather action on a rabbit
    '''
    default_rabbit = None
    def __init__(self, name: str, data: str = None):
        self.default_rabbit = name
    def run(self, rabbit = None):
        if rabbit or self.default_rabbit:
            nabweb.launch_weather(rabbit if rabbit else self.default_rabbit)
    def __repr__(self):
        return 'WeatherAction({})'.format(self.default_rabbit)

class AirQualityAction(Action):
    '''
    Launch Air Quality action on a rabbit
    '''
    default_rabbit = None
    def __init__(self, name: str, data: str = None):
        self.default_rabbit = name
    def run(self, rabbit = None):
        if rabbit or self.default_rabbit:
            nabweb.launch_airquality(rabbit if rabbit else self.default_rabbit)
    def __repr__(self):
        return 'AirQualityAction({})'.format(self.default_rabbit)

class TaichiAction(Action):
    '''
    Launch Taichi action on a rabbit
    '''
    default_rabbit = None
    def __init__(self, name: str, data: str = None):
        self.default_rabbit = name
    def run(self, rabbit = None):
        if rabbit or self.default_rabbit:
            nabweb.launch_taichi(rabbit if rabbit else self.default_rabbit)
    def __repr__(self):
        return 'TaichiAction({})'.format(self.default_rabbit)
