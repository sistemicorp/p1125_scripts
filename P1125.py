#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2020-2022 sistemicorp

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

The complete JSON REST API is viewable from the P1125 Main menu, or
http://IP_ADDRESS_OR_HOSTNAME/api/V1/browse


This file should NOT BE ALTERED.
The P1125API class is used by the example/demo scripts.
"""
import requests
from rapidjson import loads
from time import sleep


class MetaConst(type):
    def __getattr__(cls, key):
        return cls[key]

    def __setattr__(cls, key, value):
        raise TypeError


class Const(object, metaclass=MetaConst):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        raise TypeError


class StubLogger(object):
    """ stub out logger if none is provided"""
    def info(self, *args, **kwargs): pass
    def error(self, *args, **kwargs): pass
    def debug(self, *args, **kwargs): pass
    def warning(self, *args, **kwargs): pass
    def critical(self, *args, **kwargs): pass


class P1125API(Const):
    """ P1125 Constants for use with REST API

    """

    VOUT_MIN_VAL = 1800
    VOUT_MAX_VAL = 8200
    VOUT_STEP_VALUE = 100

    MAHR_SAMPLE_TIME_S = 0.01  # mAhr sampling time, seconds

    ACQUIRE_MODE_RUN = "ACQUIRE_MODE_RUN"
    ACQUIRE_MODE_SINGLE = "ACQUIRE_MODE_SINGLE"
    ACQUIRE_MODE_LIST = [
        ACQUIRE_MODE_RUN,
        ACQUIRE_MODE_SINGLE,
    ]

    TRIG_SRC_NONE = "TRIG_SRC_NONE"
    TRIG_SRC_CUR  = "TRIG_SRC_CUR"
    TRIG_SRC_D0   = "TRIG_SRC_D0"
    TRIG_SRC_D1   = "TRIG_SRC_D1"
    TRIG_SRC_A0A  = "TRIG_SRC_A0A"
    TRIG_SRC_LIST = [
        TRIG_SRC_NONE,
        TRIG_SRC_CUR,
        TRIG_SRC_D0,
        TRIG_SRC_D1,
        TRIG_SRC_A0A,
    ]

    TRIG_POS_CENTER = "TRIG_POS_CENTER"
    TRIG_POS_LEFT   = "TRIG_POS_LEFT"
    TRIG_POS_RIGHT  = "TRIG_POS_RIGHT"
    TRIG_POS_LIST = [
        TRIG_POS_CENTER,
        TRIG_POS_LEFT,
        TRIG_POS_RIGHT,
    ]

    TRIG_SLOPE_RISE = "TRIG_SLOPE_RISE"
    TRIG_SLOPE_FALL = "TRIG_SLOPE_FALL"
    TRIG_SLOPE_EITHER = "TRIG_SLOPE_EITHER"
    TRIG_SLOPE_LIST = [
        TRIG_SLOPE_RISE,
        TRIG_SLOPE_FALL,
        TRIG_SLOPE_EITHER,
    ]

    TBASE_SPAN_10MS  = "TBASE_SPAN_10MS"
    TBASE_SPAN_20MS  = "TBASE_SPAN_20MS"
    TBASE_SPAN_50MS  = "TBASE_SPAN_50MS"
    TBASE_SPAN_100MS = "TBASE_SPAN_100MS"
    TBASE_SPAN_200MS = "TBASE_SPAN_200MS"
    TBASE_SPAN_500MS = "TBASE_SPAN_500MS"
    TBASE_SPAN_1S    = "TBASE_SPAN_1S"
    TBASE_SPAN_2S    = "TBASE_SPAN_2S"
    TBASE_SPAN_5S    = "TBASE_SPAN_5S"
    TBASE_SPAN_LIST = [
        TBASE_SPAN_10MS,
        TBASE_SPAN_20MS,
        TBASE_SPAN_50MS,
        TBASE_SPAN_100MS,
        TBASE_SPAN_200MS,
        TBASE_SPAN_500MS,
        TBASE_SPAN_1S,
        TBASE_SPAN_2S,
        TBASE_SPAN_5S,
    ]

    DEMO_CAL_LOAD_NONE = "DEMO_CAL_LOAD_NONE"
    DEMO_CAL_LOAD_2M   = "DEMO_CAL_LOAD_2M_"
    DEMO_CAL_LOAD_200K = "DEMO_CAL_LOAD_200K_"
    DEMO_CAL_LOAD_20K  = "DEMO_CAL_LOAD_20K_"
    DEMO_CAL_LOAD_2K   = "DEMO_CAL_LOAD_2K_"
    DEMO_CAL_LOAD_200  = "DEMO_CAL_LOAD_200_"
    DEMO_CAL_LOAD_40   = "DEMO_CAL_LOAD_40_"
    DEMO_CAL_LOAD_20   = "DEMO_CAL_LOAD_20_"
    DEMO_CAL_LOAD_8    = "DEMO_CAL_LOAD_8_"
    DEMO_CAL_LOAD_LIST = [
        DEMO_CAL_LOAD_NONE,
        DEMO_CAL_LOAD_2M,
        DEMO_CAL_LOAD_200K,
        DEMO_CAL_LOAD_20K,
        DEMO_CAL_LOAD_2K,
        DEMO_CAL_LOAD_200,
        DEMO_CAL_LOAD_40,
        DEMO_CAL_LOAD_20,
        DEMO_CAL_LOAD_8,
    ]


class P1125(object):
    """ P1125 Class

    The complete JSON REST API is viewable from the P1125 Main menu, or
    http://IP_ADDRESS_OR_HOSTNAME/api/V1/browse

    """

    DELAY_WAIT_CALIBRATION_START_S = 15
    DELAY_WAIT_CALIBRATION_POLL_S = 2
    RETRIES_CALIBRATION_POLL = 10

    RETRIES_ACQUISITION_COMPLETE = 10
    DELAY_WAIT_ACQUISITION_POLL_S = 0.5

    REQUEST_ERRORS_MAX = 4

    def __init__(self, url="http://localhost/api/V1", loggerIn=None):
        if loggerIn: self.logger = loggerIn
        else: self.logger = StubLogger()

        self._url = url
        self._count_request_errors = 0

    def _response(self, payload):
        """ helper to send json requests

        :param payload: { "method": <"V1.method_to_call">, ["params": {"name": <value>}]}
        :return: success, result/error
                   where, success = True/False
        """
        if self._url is None: return True, {}
        if self._count_request_errors >= self.REQUEST_ERRORS_MAX:
            # TODO: tell a10 to go into a a27 reconnect state
            return False, {"error": "too many request errors"}

        _payload = {"jsonrpc": "2.0", "id": 0}
        _payload.update(payload)
        try:
            response = requests.post(self._url, json=_payload).json()
            self._count_request_errors = 0
            if "error" in response:
                self.logger.error("{} -> {}".format(_payload, response['error']))
                return False, loads(response['error'])

        except requests.exceptions.ConnectionError:
            self._count_request_errors += 1
            self.logger.error("requests.exceptions.ConnectionError")
            return False, {"error": "requests.exceptions.ConnectionError"}

        except Exception as e:
            self._count_request_errors += 1
            self.logger.error(e)
            return False, {"error": e}

        d = loads(response['result'])
        return d['success'], d

    def ping(self):
        """ Ping the P1125 and get identifiction and version information

        :return: success <True/False>, result <json/None>
        """
        payload = {"method": "V1.ping"}
        self.logger.info("{} {}".format(payload["method"], self._url))
        return self._response(payload)

    def status(self):
        payload = {"method": "V1.status"}
        self.logger.info(payload["method"])
        return self._response(payload)

    def calibrate(self, force=False):
        """ Calibrate (blocking, this can take 30-60 seconds)

        :return: success <True/False>
        """
        # determine if calibration has been done
        payload = {"method": "V1.cal_status"}
        self.logger.info(payload["method"])
        success, result = self._response(payload)
        if not success: return False, result

        cal_complete = result["cal_done"]
        if not cal_complete or force:
            self.logger.info("Calibrating... this will take a minute...")
            payload = {"method": "V1.cal"}
            self.logger.info(payload["method"])
            success, result = self._response(payload)
            if not success: return False, result

            sleep(self.DELAY_WAIT_CALIBRATION_START_S)  # big wait
            # poll to determine if calibration has completed
            retries = self.RETRIES_CALIBRATION_POLL
            while not cal_complete and retries:
                sleep(self.DELAY_WAIT_CALIBRATION_POLL_S)
                retries -= 1
                payload = {"method": "V1.cal_status"}
                success, result = self._response(payload)
                if not success or retries == 0: return False, result
                self.logger.info("{} cal_done {}".format(payload["method"], result["cal_done"]))
                cal_complete = result["cal_done"]

        return True, result

    def set_vout(self, value_mv=P1125API.VOUT_MIN_VAL):
        """ Set VOUT

        :param value_mv: <1800-8000>
        :return:  success <True/False>, result <json/None>
        """
        payload = {"method": "V1.vout", "params": {"value": value_mv}}  # in mV
        self.logger.info("{} params: {}".format(payload["method"], payload["params"]))
        return self._response(payload)

    def set_timebase(self, span):
        """ Set Timebase

        :param span: <one of TBASE_SPAN_LIST>
        :return:  success <True/False>, result <json/None>
        """
        payload = {"method": "V1.timebase", "params": {"span": span}}
        return self._response(payload)

    def set_trigger(self,
                    src=P1125API.TRIG_SRC_NONE,
                    pos=P1125API.TRIG_POS_LEFT,
                    slope=P1125API.TRIG_SLOPE_RISE,
                    level=1.0):
        """ Set Trigger

        :param src: <P1125API.TRIG_SRC_*>
        :param pos: <P1125API.TRIG_POS_*>
        :param slope: <P1125API.TRIG_SLOPE_*>
        :param level: <float in mV or uA>
        :return: success <True/False>, result <json/None>
        """
        payload = {"method": "V1.trigger", "params": {"source": src, "position": pos, "slope": slope, "level": level}}
        self.logger.info("{} params: {}".format(payload["method"], payload["params"]))
        return self._response(payload)

    def set_cal_load(self, loads=[P1125API.DEMO_CAL_LOAD_NONE]):
        """ Set Calibration Load

        - more than one load can be specified where the resultant loads are in parallel

        :param loads: [P1125API.DEMO_CAL_LOAD_*, ...]
        :return: success <True/False>, result <json/None>
        """
        payload = {"method": "V1.cal_load", "params": {"loads": loads}}
        self.logger.info("{} params: {}".format(payload["method"], payload["params"]))
        return self._response(payload)

    def acquisition_start(self, mode):
        """ Start Acquisition (Single mode)

        :param mode: <P1125API.ACQUIRE_MODE_*>
        :return: success <True/False>, result <json/None>
        """
        payload = {"method": "V1.acquire_start", "params": {"mode": mode}}
        self.logger.info(payload["method"])
        return self._response(payload)

    def acquisition_stop(self):
        """ Stop/Abort Acquisition

        :return: success <True/False>, result <json/None>
        """
        payload = {"method": "V1.acquire_stop"}
        self.logger.info(payload["method"])
        return self._response(payload)

    def acquisition_complete(self, retries=RETRIES_ACQUISITION_COMPLETE):
        """ Poll Acquisistion Complete

        :param retries: number of polling retries
        :return: success <True/False>, result <json/None>
        """
        triggered = False
        retries = retries
        while not triggered and retries:
            sleep(self.DELAY_WAIT_ACQUISITION_POLL_S)
            retries -= 1
            payload = {"method": "V1.acquire_is_triggered"}
            success, result = self._response(payload)
            if not success or retries == 0:
                self.logger.error("{} triggered {}".format(payload["method"], result))
                return False, result
            self.logger.info("{} triggered {}".format(payload["method"], result["triggered"]))
            triggered = result["triggered"]

        return triggered, result

    def acquisition_get_data(self):
        """ Get Acquisition Data

        :return: success <True/False>, result <json/None>
        """
        payload = {"method": "V1.plot_data"}
        self.logger.info(payload["method"])
        return self._response(payload)

    def intcurr_set(self, time_stop_s):
        """ Set Integrated Current settings
        - note that integrated current measurement is limited internally to a maximum
          number of samples.  Data collection will stop when that limit is reached.

        :param time_stop_s: stop time in seconds, example 3600 for 1 hour
        :return: success <True/False>, result <json/None>
        """
        payload = {"method": "V1.intcurr_set", "params": {"time_stop_s": time_stop_s}}
        self.logger.info(payload["method"])
        return self._response(payload)

    def intcurr_complete(self):
        """ Get Integrated Current Acquisition is Complete

        :return: success <True/False>, result <json/None>
        """
        payload = {"method": "V1.intcurr_complete"}
        self.logger.info(payload["method"])
        return self._response(payload)

    def intcurr_data(self):
        """ Get Integrated Current Data

        - (JSON)Result Dictionary Keys:
            'success': <True|False>
            'time_s': <acquisition_time_seconds>
            'time_stop_s': <acquisition_stop_time_seconds>,
            'ucoulombs': <total_micro_coulombs>,
            'samples': <number_of_samples>,
            'mahr': <mAhr>,
            'plot': <'t': [...],         # time, seconds
                     'i': [...],         # current, micro-amps
                     'i_max': [...]>     # max current, micro-amps
                     'plot_d0': {        # D0 events
                         't': [...]      # time, seconds
                         'd0: [...] },   # d0 value
                     'plot_d1': {        # D1 events
                         't': [...]      # time, seconds
                         'd1: [...] },   # d1 value
                     'plot_trig': {      # trigger events
                         't': [...]      # time, seconds
                         'trig: [...] }, # trigger value

        - the integrated current acquisition is complete when time_s > time_stop_s.
        - use intcurr_complete() to poll for acquisition is complete

        :return: success <True/False>, result <json/None>
        """
        payload = {"method": "V1.intcurr_data"}
        self.logger.info(payload["method"])
        return self._response(payload)

    def probe(self, connect=True, hard_connect=False):
        """ Set Probe Connect

        If the probe is not connected, connecting will fail.  The P1125 can detect
        whether the probe is connected or not.  See probe_status()

        Setting hard_connect will bypass the soft start feature.

        :param connect: <True/False>
        :param hard_connect: <True/False>
        :return: success <True/False>, result <json/None>
        """
        payload = {"method": "V1.probe_connect", "params": {"value": connect, "hard_connect": hard_connect}}
        self.logger.info("{} params: {}".format(payload["method"], payload["params"]))
        return self._response(payload)

    def probe_status(self):
        """ Get Probe Status

        :return: success <True/False>, result <json/None>
        """
        payload = {"method": "V1.probe_status"}
        self.logger.info("{}".format(payload["method"]))
        return self._response(payload)

    def shutdown(self, restart=False):
        """ Shutdown P1125

        :param restart: <True/False>, if set the P1125 will reboot/restart
        :return: success <True/False>, result <json/None>
        """
        payload = {"method": "V1.shutdown", "params": {"restart": restart}}
        self.logger.info("{}".format(payload["method"]))
        return self._response(payload)
