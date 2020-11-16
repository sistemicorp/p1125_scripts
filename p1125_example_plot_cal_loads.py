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
http://IP_ADDRESS_OR_HOSTNAME/api/V1/browse

Run this file,
    $python3 p1125_example_plot_cal_loads.py

Requirements:
1) Python 3.6+ and bokeh 2.2.0 (pip3 install bokeh) or greater installed.
2) Change line 47 to suit your environment.
3) Chrome browser.

Notes:
1) Calibration loads are only attached to the supply when the probe is DISCONNECTED.

"""
import logging
from bokeh.layouts import layout
from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource

from p1125api import P1125, P1125API

logger = logging.getLogger()
logger.setLevel(logging.INFO)
FORMAT = "%(asctime)s: %(filename)20s: %(funcName)25s %(lineno)4s - %(levelname)-5.5s : %(message)s"
formatter = logging.Formatter(FORMAT)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

# NOTE: Change to P1125 IP address or hostname
P1125_URL = "http://IP_ADDRESS_OR_HOSTNAME/api/V1"

if "IP_ADDRESS_OR_HOSTNAME" in P1125_URL:
    logger.error("Please set P1125_URL with valid IP/Hostname")
    exit(1)

# bokeh plot setup
plot = figure(toolbar_location="above", y_range=(0.1, 1000000), y_axis_type="log")
doc_layout = layout()

VOUT = 4000  # mV, output voltage
SPAN = P1125API.TBASE_SPAN_100MS

#                      loads to cycle thru,  line name,   color
LOADS_TO_PLOT = [([P1125API.DEMO_CAL_LOAD_200K], "200k", "green"),
                 ([P1125API.DEMO_CAL_LOAD_20K],  "20k",  "blue"),
                 ([P1125API.DEMO_CAL_LOAD_2K],   "2k",   "yellow"),
                 ([P1125API.DEMO_CAL_LOAD_200],  "200",  "black"),

                 # loads in parallel
                 ([P1125API.DEMO_CAL_LOAD_200K, P1125API.DEMO_CAL_LOAD_20K], "200k//20k", "red"),
                 ]


def plot_add(data, name, color="green"):
    """ Add line to the plot

    :param data: The data to plot in bokeh format, { "x": [...], "y": [...] }
    :param name: string name
    :param color: string color, can be 'red', 'blue', or "#ABC123", ...
    :return: None
    """
    source = ColumnDataSource(data=data)
    plot.line(x="t", y="i", line_width=2, source=source, color=color, legend_label=name)


def plot_fini():
    """ Plot the data, opens web browser with plot

    :return: None
    """
    doc_layout.children.append(plot)
    show(doc_layout)


def main():
    """
    An example sequence of commands to make a measurement with the P1125 REST API.

    The internal Calibration loads will be used to plot essentially DC currents of various magnitudes.
    Since internal loads are used, the Probe is not connected.
    """
    p1125 = P1125(url=P1125_URL, loggerIn=logger)

    # check if the P1125 is reachable
    success, result = p1125.ping()
    logger.info("ping: {}".format(result))
    if not success: return False

    success, result = p1125.status()
    logger.info("status: {}".format(result))
    if not success: return False

    success, result = p1125.probe(connect=False)
    logger.info("probe: {}".format(result))
    if not success: return False

    success, result = p1125.calibrate()
    logger.info("calibrate: {}".format(result))
    if not success: return False

    success, result = p1125.set_vout(VOUT)
    logger.info("set_vout: {}".format(result))
    if not success: return False

    success, result = p1125.set_timebase(SPAN)
    logger.info("set_timebase: {}".format(result))
    if not success: return False

    success, result = p1125.set_trigger(src=P1125API.TRIG_SRC_NONE,
                                        pos=P1125API.TRIG_POS_LEFT,
                                        slope=P1125API.TRIG_SLOPE_RISE,
                                        level=1.0)
    logger.info("set_trigger: {}".format(result))
    if not success: return False

    # loop thru all the loads to plot
    for load, name, color in LOADS_TO_PLOT:
        logger.info(load)

        success, result = p1125.set_cal_load(loads=load)
        logger.info("set_cal_load: {}".format(result))
        if not success: return False

        success, result = p1125.acquisition_start(mode=P1125API.ACQUIRE_MODE_SINGLE)
        logger.info("acquisition_start: {}".format(result))
        if not success: return False

        success, result = p1125.acquisition_complete()
        logger.info("acquisition_complete: {}".format(result))
        if not success: return False

        success, result = p1125.acquisition_get_data()
        #logger.info("acquisition_get_data: {}".format(result))
        if not success: return False
        result.pop("success")
        plot_add(result, name, color)

    # turn off any loads
    success, result = p1125.set_cal_load(loads=[P1125API.DEMO_CAL_LOAD_NONE])
    logger.info("set_cal_load: {}".format(result))
    if not success: return False

    plot_fini()
    return True


if __name__ == "__main__":
    success = main()
    if not success: logger.error("failed")
