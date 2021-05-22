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

The P1125 GUI can be open during the running of this script.

The complete JSON REST API is viewable from the Main menu, or
http://p1125_hostname/api/V1/browse

Run this file,
    $python3 p1125_example_mahrs.py

Requirements:
1) Python 3.6+ and bokeh 2.2.0 (pip3 install bokeh) or greater installed.
2) Change line 46 to suit your environment.
3) Chrome browser.

--- !!! WARNING !!! ---
if CONNECT_PROBE is True, this example connects the PROBE at VOUT_LIST mV

"""
import time
import logging
from bokeh.layouts import layout
from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.palettes import viridis

from P1125 import P1125, P1125API

logger = logging.getLogger()
logger.setLevel(logging.INFO)
FORMAT = "%(asctime)s: %(filename)25s: %(funcName)25s %(lineno)4s - %(levelname)-5.5s : %(message)s"
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

p1125 = P1125(url=URL, loggerIn=logger)

plot = figure(title="Current vs Time")
plot.xaxis.axis_label = "Time (sec)"
plot.yaxis.axis_label = "Current (micro-Amps)"

plot_mahr = figure(title="mAhr vs Supply Voltage")
plot_mahr.xaxis.axis_label = "Supply (mV)"
plot_mahr.yaxis.axis_label = "Average mAhr"

doc_layout = layout()

VOUT_LIST = [3000, 2800, 2600, 2400, 2200]      # list of voltages over which to measure
CONNECT_PROBE = True               # set to True to attach probe, !! Warning: check VOUT setting !!
TIME_STOP_S = 30                   # seconds over which to measure the mAhr
intcurr_results = []               # list of results for every VOUT
setup_done = True                  # set to true if target is powered and ready

vout_colors = viridis(len(VOUT_LIST))
color_key_value_pairs = dict(zip(VOUT_LIST, vout_colors))


def plot_add(data, name, color="green"):
    """ Add line to the plot

    :param data: The data to plot in bokeh format, { "x": [...], "y": [...] }
    :param name: string name
    :param color: string color, can be 'red', 'blue', or "#ABC123", ...
    :return: None
    """
    source = ColumnDataSource(data=data)
    plot.line(x="t", y="i", line_width=2, source=source, color=color, legend_label=name)


def plot_add_mahr(data, name, color="green"):
    """ Add line to the plot

    :param data: The data to plot in bokeh format, { "x": [...], "y": [...] }
    :param name: string name
    :param color: string color, can be 'red', 'blue', or "#ABC123", ...
    :return: None
    """
    source = ColumnDataSource(data=data)
    plot_mahr.line(x="vout", y="mahr", line_width=2, source=source, color=color, legend_label=name)


def plot_fini():
    """ Plot the data, opens web browser with plot

    :return: None
    """
    doc_layout.children.append(plot)
    doc_layout.children.append(plot_mahr)
    show(doc_layout)


def main():
    """
    An example sequence of commands to make a measurement with the P1125 REST API

    This example measures the mAhr used by the target over a list of voltages.
    The target power system, if it has a switched mode buck/boost, will have different
    efficiency at different input voltages.  This test will quantify that efficiency.
    """
    # check if the P1125 is reachable
    success, result = p1125.ping()
    logger.info(result)
    if not success: return False

    success, result = p1125.status()
    logger.info(result)
    if not success: return False

    success, result = p1125.intcurr_set(time_stop_s=TIME_STOP_S)
    if not success:
        logger.error(result)
        return False

    if not setup_done:
        success, result = p1125.probe(connect=False)
        if not success: return False

        success, result = p1125.calibrate()
        if not success: return False

        success, result = p1125.set_vout(VOUT_LIST[0])
        if not success: return False

        # connect probe
        success, result = p1125.probe(connect=CONNECT_PROBE)
        if not success: return False

        time.sleep(2)  # change as required...

    # for every vout, measure the mAhrs
    for vout in VOUT_LIST:
        success, result = p1125.set_vout(vout)
        if not success: return False

        # pause here to let system power up to a certain state, change to suit your need
        time.sleep(1)

        success, result = p1125.acquisition_start(mode=P1125API.ACQUIRE_MODE_RUN)
        if not success: return False

        logger.info("Time until data is ready... {:4d} seconds".format(TIME_STOP_S))
        count_one_second = TIME_STOP_S
        while count_one_second > 0:
            count_one_second -= 1
            time.sleep(1)
            if count_one_second % 10 == 0:
                logger.info("Time until data is ready... {:4d} seconds".format(count_one_second))

        # check and see if Integrated Current is complete
        while True:
            success, intcurr_result = p1125.intcurr_data()
            logger.info("{}, data collection time: {} / {}".format(intcurr_result["success"],
                                                                   intcurr_result["time_s"],
                                                                   intcurr_result["time_stop_s"]))
            if not success: return False

            if intcurr_result["time_s"] >= intcurr_result["time_stop_s"]: break

            logger.info("Time until data is ready... extra {:4d} seconds".format(count_one_second))
            count_one_second += 1
            time.sleep(1)

        success, result = p1125.acquisition_stop()
        if not success: return False

        intcurr_result["vout"] = vout  # tag this result with the voltage used, helpful later
        intcurr_results.append(intcurr_result)

    success, result = p1125.probe(connect=False)
    logger.info(result)
    if not success: return False

    mahrs = {"vout": [], "mahr": []}
    for intcurr_result in intcurr_results:
        vout = intcurr_result["vout"]
        # only plotting current for demo, can also plot D0/D1/Trig events
        logger.info("VOUT: {:4d} mV, t: {}".format(vout, intcurr_result["plot"]['t'][0:10]))
        logger.info("               i: {}".format(intcurr_result["plot"]['i'][0:10]))
        plot_add(intcurr_result["plot"], "{}mV".format(vout), color=color_key_value_pairs[vout])

        mahrs["vout"].append(vout)
        mahrs["mahr"].append(intcurr_result["mahr"])

    logger.info(mahrs)
    plot_add_mahr(mahrs, "mAhr", "green")

    plot_fini()
    return True


if __name__ == "__main__":
    try:
        success = main()

    except Exception as e:
        logger.error(e)
        success = False

    finally:
        # turn off any loads
        p1125.set_cal_load(loads=[P1125API.DEMO_CAL_LOAD_NONE])
        p1125.probe(connect=False)

    if not success: logger.error("failed")
