#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2020 sistemicorp

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

A minimal example showing how to take a measurement via the P1125 REST API.

The P1125 GUI can be open during the running of this script.

The complete JSON REST API is viewable from the P1125R Main menu, or
http://IP_ADDRESS_OR_HOSTNAME/api/V1/browse

Run this file,
    $python3 p1125_example_mahrs_logging.py

Requirements:
1) Python 3.6+ and bokeh 2.3.0 (pip3 install bokeh) or greater installed.
2) Change line 61 to suit your environment.
3) Chrome browser.

--- !!! WARNING !!! ---
if CONNECT_PROBE is True, this example connects the PROBE at VOUT mV

"""
import os
import time
import logging
import datetime

from P1125 import P1125, P1125API

logger = logging.getLogger()
logger.setLevel(logging.INFO)
FORMAT = "%(asctime)s: %(funcName)25s %(lineno)4s - %(levelname)-5.5s : %(message)s"
formatter = logging.Formatter(FORMAT)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

# NOTE: Change to P1125 IP address or hostname
P1125_URL = "p1125-####.local"  # for example, p115-a12b.local, or 192.168.0.123
P1125_API = "/api/V1"
URL = "http://" + P1125_URL + P1125_API

if "p1125-####.local" in P1125_URL:
    logger.error("Please set P1125_URL with valid IP/Hostname")
    exit(1)

# Change these parameters to suit your needs:
VOUT = 3000                   # mV, output voltage, 2000-8000 mV
CONNECT_PROBE = False         # set to True to attach probe, !! Warning: check VOUT setting !!
TIME_CAPTURE_WINDOW_S = 30    # seconds over which to measure the AVERAGE mAhr
TIME_TOTAL_RUN_S = 30 * 2     # seconds, total run time of the log
LOG_FILE_PATH = "./"          # path to output file, use USB stick if possible

WRITE_PLOT_DATA = True        # flag for write_data()
WAIT_POLLING_TIME_S = 0.5     # time to wait between polls whilst waiting for TIME_CAPTURE_WINDOW_S to complete

p1125 = P1125(url=URL, loggerIn=logger)
filename = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".py"
setup_done = False            # set flag if target is manually setup and ready to go

def wait_for_measurement():
    """ helper function to log waiting around for data to be ready
    - a combination of waiting and polling
    - this function is called after p1125.acquisition_start(...)

    :return: success <True/False>, data
    """
    # pre-waiting here, the acquisition was just kicked off, leave the P1125 alone
    time.sleep(1)

    logger.info("Time until data is ready... {:4d} seconds".format(TIME_CAPTURE_WINDOW_S))
    count_one_second = TIME_CAPTURE_WINDOW_S
    while count_one_second > 0:
        count_one_second -= 1
        time.sleep(1)
        if count_one_second % 10 == 0:
            logger.info("Time until data is ready... {:4d} seconds".format(count_one_second))

    # almost time, poll to check and see if Integrated Current is complete
    while True:  # TODO: add infinite loop protection...
        success, intcurr_complete = p1125.intcurr_complete()
        logger.info("{}, data collection time: {} / {} ({})".format(intcurr_complete["success"],
                                                               intcurr_complete["time_s"],
                                                               intcurr_complete["time_stop_s"],
                                                               intcurr_complete["complete"]))
        if not success: return False

        if intcurr_complete["complete"]:
            # the waiting loop is stopped here, TIME_CAPTURE_WINDOW_S has completed...
            return True

        logger.info("Time until data is ready... extra {:6.1f} seconds".format(count_one_second))
        count_one_second += WAIT_POLLING_TIME_S
        time.sleep(WAIT_POLLING_TIME_S)

    logger.error("should never get here")
    return False, None


def write_data_header(ping, status):
    """ write output log file header

    :param status: p1125 information
    :return: success <True/False>
    """
    try:
        with open(os.path.join(LOG_FILE_PATH, filename), "w+") as f:
            f.write("# This file is auto-generated by p1125_example_mahrs_logging.py\n".format(filename))
            f.write("# {}\n".format(filename))
            f.write("p1125_ping = {}\n".format(ping))
            f.write("p1125_status = {}\n".format(status))
            f.write("p1125_settings = {{'VOUT': {}, 'TIME_CAPTURE_WINDOW_S': {}, 'TIME_TOTAL_RUN_S': {}, 'CONNECT_PROBE': {}}}\n".format(VOUT,
                    TIME_CAPTURE_WINDOW_S, TIME_TOTAL_RUN_S, CONNECT_PROBE))
            f.write("# NOTE: Might have to add missing last ']' if program was interrupted\n")
            f.write("p1125_data = [\n".format(filename))

    except Exception as e:
        logger.error(e)
        return False

    return True


def write_data(intcurr_result):
    """ write data
    - create a list of dicts with data

    - available fields are, use print(intcurr_result) to see all,
    {'success': True,
     'time_s': 30.8795,
     'time_stop_s': 30,
     'ucoulombs': 2517.936,
     'samples': 1424,
     'mahr': 0.0815407,
     'plot': {'t': [0, 0.01278125, 0.0255625, ... ],
              'i': [54.54963, 319.9456, 26.60415, ...],
              'i_max': [64.54963, 419.9456, 36.60415, ...]},
     'plot_d0': {'t': [], 'd0': []},
     'plot_d1': {'t': [], 'd1': []},
     'plot_trig': {'t': [], 'trig': []}
    }
    - save only the data you need...

    :param intcurr_result: dict of data
    :return: success <True/False>
    """
    # uncomment this to see what fields are available
    # logger.info(intcurr_result)

    max_window_current_ua = max(intcurr_result["plot"]["i_max"])

    try:
        with open(os.path.join(LOG_FILE_PATH, filename), "a+") as f:
            dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            f.write("{{'datetime': '{}', 'time_s': {}, 'mAhr': {}, 'i_max_ua': {}, 'samples': {},".format(
                    dt,
                    intcurr_result["time_s"],
                    intcurr_result["mahr"],
                    max_window_current_ua,
                    intcurr_result["samples"]))

            if WRITE_PLOT_DATA:  # or if intcurr_result["iavg_max_ua"/"mahr"] > YOUR_THRESHOLD_HERE
                f.write(f"'plot': {intcurr_result['plot']},")

                # NOTE: plot data may be reduced, successive results with near same values removed, to save memory

            # TODO: add more stuff as required...

            f.write("},\n")

    except Exception as e:
        logger.error(e)
        return False

    return True


def write_data_footer():
    """ write footer to log file

    :return: success <True/False>
    """
    try:
        with open(os.path.join(LOG_FILE_PATH, filename), "a+") as f:
            f.write("]\n")

    except Exception as e:
        logger.error(e)
        return False

    return True


def main():
    """
    An example sequence of commands to make a measurement with the P1125 REST API

    This script is for gather measurements to a file over a long long period of time.
    There are three functions that write data to the file,
       write_data_header()
       write_data()
       write_data_footer()

    Modify the write_data_*() functions to format the data file to suit your needs.
    """
    # check if the P1125 is reachable
    success, ping = p1125.ping()
    logger.info(ping)
    if not success: return False

    success, status = p1125.status()
    logger.info(status)
    if not success: return False

    success = write_data_header(ping, status)
    if not success: return False

    if status["aqc_in_progress"]:  # stop any previously running acquisition
        success, result = p1125.acquisition_stop()
        if not success: return False

    success, result = p1125.calibrate()
    logger.info(result)
    if not success: return False

    success, result = p1125.intcurr_set(time_stop_s=TIME_CAPTURE_WINDOW_S)
    logger.info(result)
    if not success: return False

    if not setup_done:
        success, result = p1125.probe(connect=False)
        logger.info(result)
        if not success: return False

    success, result = p1125.set_vout(VOUT)
    logger.info(result)
    if not success: return False

        time.sleep(1)

        # !!!!!!!!!!!! CHANGE THIS SECTION TO SUIT YOUR TARGET !!!!!!!!!!!!!!!!!!!

    # connect probe - ! make sure VOUT is right !
    success, result = p1125.probe(connect=CONNECT_PROBE)
    logger.info(result)
    if not success: return False

    # test load, use when CONNECT_PROBE=False, remember to clear this load, see below
    success, result = p1125.set_cal_load(loads=[P1125API.DEMO_CAL_LOAD_2K])  # change load to experiment
    logger.info("set_cal_load: {}".format(result))
    if not success: return False

    # pause here to let system power up to a certain state, change to suit your need
    time.sleep(1)

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    start_time = datetime.datetime.now()

    try:
        success, result = p1125.acquisition_start(mode=P1125API.ACQUIRE_MODE_RUN)
        logger.info(result)
        if not success: return False

        while True:
            success = wait_for_measurement()
            if not success: return False

            success, intcurr_result = p1125.intcurr_data()
            if not success: return False

            success, result = p1125.acquisition_stop()
            if not success: return False

            # restart the acquisition NOW, to miss as little as possible,
            # write the data out below, while next acquisition is running
            duration = datetime.datetime.now() - start_time
            if duration.total_seconds() < TIME_TOTAL_RUN_S:
                success, result = p1125.acquisition_start(mode=P1125API.ACQUIRE_MODE_RUN)
                logger.info(result)
                if not success: return False

            else:
                break  # but must still write out the data from last acquisition

            # data is ready... write to file
            success = write_data(intcurr_result)
            if not success: return False

        # data is ready... write to file
        success = write_data(intcurr_result)
        if not success: return False

    except Exception as e:
        logger.error(e)

    #success, result = p1125.set_cal_load(loads=[])  # reset

    success, result = p1125.probe(connect=False)
    logger.info(result)
    if not success: return False

    success = write_data_footer()
    if not success: return False

    return True


if __name__ == "__main__":

    try:
        success = main()

        if success:
            print("Please now run:")
            print("bokeh serve --show p1125_example_mahrs_logging_plot.py --args -f {}".format(filename))

    # catch CTRL-C
    except Exception as e:
        p1125.probe(connect=False)
        p1125.acquisition_stop()
        success = False
        logger.error(e)

    if not success: logger.error("failed")
