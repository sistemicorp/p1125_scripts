#!/usr/bin/python
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

The P1125 GUI can be open during the running of this script.

The complete JSON-RPC API is viewable from the Main menu, or
http://p1125_hostname/api/V1/browse

Run this file,
    $python3 p1125_example_plot.py

Requirements:
1) Python 3.6+ and bokeh 2.3.0 (pip3 install bokeh) or greater installed.
2) Change line 61 to suit your environment.
3) Chrome browser.

--- !!! WARNING !!! ---
if CONNECT_PROBE is True, this example connects the PROBE at 3000 (VOUT) mV

"""
import logging
from bokeh.layouts import layout
from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool, BoxZoomTool, ResetTool, UndoTool, PanTool, WheelZoomTool

from P1125 import P1125, P1125API

logger = logging.getLogger()
logger.setLevel(logging.INFO)
FORMAT = "%(asctime)s: %(filename)22s: %(funcName)25s %(lineno)4s - %(levelname)-5.5s : %(message)s"
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

plot = figure(toolbar_location="above", y_range=(0.1, 1000000), y_axis_type="log")
plot.xaxis.axis_label = "Time (mS)"
plot.yaxis.axis_label = "Current (uA)"

doc_layout = layout()

VOUT = 4000                       # mV, output voltage, 2000-8000 mV
SPAN = P1125API.TBASE_SPAN_100MS  # set timebase
CONNECT_PROBE = False             # set to True to attach probe, !! Warning: check VOUT setting !!


def plot_add(data, name, color="green"):
    """ Add line to the plot

    :param data: The data to plot in bokeh format, { "x": [...], "y": [...] }
    :param name: string name
    :param color: string color, can be 'red', 'blue', or "#ABC123", ...
    :return: line object to be included in Hover tool
    """
    source = ColumnDataSource(data=data)
    return plot.line(x="t", y="i", line_width=2, source=source, color=color, legend_label=name)


def plot_fini():
    """ Plot the data, opens web browser with plot

    :return: None
    """
    doc_layout.children.append(plot)
    show(doc_layout)


def main():
    """
    An example sequence of commands to make a measurement with the P1125 REST API

    """
    p1125 = P1125(url=URL, loggerIn=logger)

    # check if the P1125 is reachable
    success, result = p1125.ping()
    logger.info(result)
    if not success: return False

    success, result = p1125.status()
    logger.info(result)
    if not success: return False

    success, result = p1125.probe(connect=False)
    logger.info(result)
    if not success: return False

    success, result = p1125.calibrate()
    logger.info(result)
    if not success: return False

    success, result = p1125.set_vout(VOUT)
    logger.info(result)
    if not success: return False

    success, result = p1125.set_timebase(SPAN)
    logger.info(result)
    if not success: return False

    success, result = p1125.set_trigger(src=P1125API.TRIG_SRC_NONE,
                                        pos=P1125API.TRIG_POS_LEFT,
                                        slope=P1125API.TRIG_SLOPE_RISE,
                                        level=1)
    logger.info(result)
    if not success: return False

    # connect probe
    success, result = p1125.probe(connect=CONNECT_PROBE)
    logger.info(result)
    if not success: return False

    success, result = p1125.acquisition_start(mode=P1125API.ACQUIRE_MODE_SINGLE)
    logger.info(result)
    if not success: return False

    success, result = p1125.acquisition_complete()
    logger.info(result)
    if not success: return False

    success, result = p1125.probe(connect=False)
    logger.info(result)
    if not success: return False

    success, result = p1125.acquisition_get_data()
    #logger.info(result)  # a lot of data here, uncomment to explore
    if not success: return False
    result.pop("success")  # bokeh requires dict to have all fields same length, 'success' is not part of data
    line = plot_add(result, "MyPlot", "blue")

    ht = HoverTool(
        tooltips=[("Current", "@i{0.00} uA"), ("Time", "@t{0.00} mS")],
        mode='vline',  # display a tooltip whenever the cursor is vertically in line with a glyph
        show_arrow=True,
        renderers=[line],
    )
    plot.tools = [ht, BoxZoomTool(), WheelZoomTool(dimensions="width"), ResetTool(), UndoTool(), PanTool(dimensions="width")]

    plot_fini()
    return True


if __name__ == "__main__":
    success = main()
    if not success: logger.error("failed")
