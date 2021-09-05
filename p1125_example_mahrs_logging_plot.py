#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2020-2021, sistemicorp

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

Run this file,
    $bokeh serve --show p1125_example_mahrs_logging_plot.py --args -f <MAHR_LOGGING_FILE>.py

Where: <MAHR_LOGGING_FILE> is file created with p1125_example_mahrs_logging.py

Requirements:
1) Python 3.6+ and bokeh 2.3.0 (pip3 install bokeh) or greater installed.
2) Chrome browser.

Notes:
1) mAhr is plotted in mA, and other currents are plotted in uA

"""
import os
import argparse
import logging
import importlib.util
import datetime
from bokeh.layouts import row, column
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, Div
from bokeh.models.widgets.inputs import Select
from bokeh.events import DoubleTap
from bokeh.models import HoverTool, BoxZoomTool, ResetTool, UndoTool, PanTool, WheelZoomTool

logger = logging.getLogger()
logger.setLevel(logging.INFO)
FORMAT = "%(asctime)s: %(funcName)25s %(lineno)4s - %(levelname)-5.5s : %(message)s"
formatter = logging.Formatter(FORMAT)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

PLOT_MIN = 0.01
PLOT_MAX = 1000000

G = {  # global variables
    "select_options": [],  # holds select drop down options, as tuple (idx, name)
    "d": None              # data for the real time plot ColumnDataSource()
}


# this plot for the logging scalor values, 'mAhr', 'iavg_max_ua', etc
plot = figure(toolbar_location="above",
              y_range=(PLOT_MIN, PLOT_MAX),
              y_axis_type="log",
              x_axis_type='datetime',
              tools="tap,pan,wheel_zoom,box_zoom,reset",
              width=800)
plot.xaxis.formatter=DatetimeTickFormatter(minutes=["%m/%d %H:%M"])
plot.xaxis.axis_label = "Datetime"


source_sel = ColumnDataSource(data=dict(x=[], y=[]))
plot.line(x="t", y="y", line_width=6, line_alpha=0.6, source=source_sel)  # select line


def cb_plot(event):
    # user selected a point on the plot, use that point to determine what real time data to plot
    logger.info("{} {}".format(event.x, event.y))
    dt = datetime.datetime.utcfromtimestamp(int(event.x / 1000))
    logger.info(dt)

    # find the closest real data and align to that
    # TODO: find the closest
    item = None
    for item in G["select_options"]:
        # recall that G["select_options"] only has items with plot data, so the user
        # can't select data points that have no data.  So if the log file has filtered
        # data, and not all points have data, then the user can't select - cause there is no data

        sel_dt = datetime.datetime.strptime(item[1], '%Y%m%d-%H%M%S')
        if sel_dt > dt: break  # found closest data point

    if item:  # only allows items with plot data
        key = int(item[0])
        source_rt.data = G['d'].p1125_data[key]['plot']
        source_sel.data = {'t': [sel_dt, sel_dt], 'y': [PLOT_MIN, PLOT_MAX]}


plot.on_event(DoubleTap, cb_plot)

# this plot for the realtime data, if available
plot_rt = figure(toolbar_location="above", y_range=(PLOT_MIN, PLOT_MAX), y_axis_type="log", width=800)
source_rt = ColumnDataSource(data=dict(x=[], y=[]))
l = plot_rt.line(x="t", y="i", line_width=2, source=source_rt, legend_label="Current (uA)")
plot_rt.line(x="t", y="i_max", line_width=2, source=source_rt, legend_label="Peak Current (uA)", color="red")
plot_rt.xaxis.axis_label = "Time (S)"

ht = HoverTool(
    tooltips=[("Current", "@i{0.00} uA"), ("Time", "@t{0.00} S")],
    mode='vline',  # display a tooltip whenever the cursor is vertically in line with a glyph
    show_arrow=True,
    renderers=[l],
)
plot_rt.tools = [ht, BoxZoomTool(), WheelZoomTool(dimensions="width"), ResetTool(), UndoTool(),
              PanTool(dimensions="width")]

doc_layout = curdoc()


def extract_data(d, keys):
    """ Extract key for plotting
    - create a dict of 't' (time) and 'y' for plotting
    - keys can be one of 'mAhr' or 'iavg_max_ua', or others, it depends on what is available

    :param keys: list of keys to extract
    :param d: always p1125_log.p1125_data
    :return: None on error, dict on success
    """
    data = {"t": []}
    for key in keys: data[key] = []
    for item in d:
        dt = datetime.datetime.strptime(item['datetime'], '%Y%m%d-%H%M%S')
        data['t'].append(dt)

        for key in keys:
            if key not in item:
                logger.error("invalid key {}, not in {}".format(key, item))
                return None

            data[key].append(item[key])

    return data


def callback(attr, old, new):
    logger.info("{} {} {}".format(attr, old, new))
    key = int(new)
    logger.info(key)
    #logger.info(G['d'].p1125_data[key])
    source_rt.data = G['d'].p1125_data[key]['plot']

    dt = datetime.datetime.strptime(G['d'].p1125_data[key]['datetime'], '%Y%m%d-%H%M%S')
    logger.info(dt)
    source_sel.data = {'t': [dt, dt], 'y': [PLOT_MIN, PLOT_MAX]}


def create_select_widget(d):
    """  Add a Select widget that has a list of all the datetimes from the P1125 logging data
    - this allows the user to select which datetime to plot the detail of

    :param d: always p1125_log.p1125_data
    :return: nothing
    """
    for idx, item in enumerate(d):

        # TODO: you can add filtering here, for example, only add items that exceed a certain
        #       maximum mahr...
        #if item['iavg_max_ua'] > YOUR_VALUE:

        if 'plot' in item:  # only put in options that have plot data
            G["select_options"].append(('{}'.format(idx), '{}'.format(item['datetime']),))

    s = Select(options=G["select_options"], value=None, title="Select Date",)
    s.on_change("value", callback)

    return s


def main():
    """
    Companion script to p1125_example_mahrs_logging.py

    Extracts data from the logging file and plots it.
    """
    epilog = """
    DO NOT RUN p1125_example_mahrs_logging_plot.py directly.
    
    Usage examples:
       bokeh serve --show p1125_example_mahrs_logging_plot.py --args -f 20201027-170242.py
    """
    parser = argparse.ArgumentParser(description='p1125r_example_mahrs_logging_plot file parser, used with "boke serve"',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=epilog)
    parser.add_argument("-f", "--file", dest="file", action='store', required=True, help='log file to parse/plot')
    args = parser.parse_args()

    if not os.path.exists(args.file):
        logger.error("file does not exist, {}".format(args.file))
        exit(1)
    logger.info(args.file)

    try:
        spec = importlib.util.spec_from_file_location("p1125_log", args.file)
        G['d'] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(G['d'])

    except Exception as e:
        logger.error(e)
        return False

    logger.info(G['d'].p1125_ping)
    logger.info(G['d'].p1125_status)
    logger.info(G['d'].p1125_settings)
    #logger.info(G['d'].p1125_data)  # uncomment to see imported fields/data

    plot_data = extract_data(G['d'].p1125_data, ['mAhr', 'i_max_ua'])
    if plot_data is not None:
        source = ColumnDataSource(data=plot_data)
        plot.circle(x="t", y="mAhr", size=5, source=source, color="green", legend_label='mAhr')
        l = plot.line(x="t", y="mAhr", line_width=2, source=source, color="green", legend_label='mAhr')

        plot.circle(x="t", y='i_max_ua', size=5, source=source, color="red", legend_label="Max uA")
        plot.line(x="t", y='i_max_ua', line_width=2, source=source, color="red", legend_label="Max uA")

        ht = HoverTool(
            tooltips=[("mAhr", "@mAhr{0.00}"), ("Max", "@i_max_ua{0.00} uA"), ("Time", "@t{%m/%d %H:%M}") ],
            mode='vline',  # display a tooltip whenever the cursor is vertically in line with a glyph
            formatters={'@t': 'datetime', },
            show_arrow=True,
            renderers=[l],
        )
        plot.tools = [ht, BoxZoomTool(), WheelZoomTool(dimensions="width"), ResetTool(), UndoTool(), PanTool(dimensions="width")]

    else:
        logger.error("extract_data failed")

    s = create_select_widget(G['d'].p1125_data)

    hdr1 = Div(text="""Setup: VOUT {} mV, TIME_CAPTURE_WINDOW_S {} sec, {} sec""".format(
            G['d'].p1125_settings["VOUT"], G['d'].p1125_settings["TIME_CAPTURE_WINDOW_S"], G['d'].p1125_settings["TIME_TOTAL_RUN_S"]))

    hdr2 = Div(text="""P1125: {}, {}, {}, {} degC""".format(
            G['d'].p1125_ping["version"], G['d'].p1125_ping["rpi_serial"], G['d'].p1125_ping["url"],
            G['d'].p1125_status["temperature_degc"]))

    # init the first data to plot
    source_rt.data = G['d'].p1125_data[0]['plot']
    dt = datetime.datetime.strptime(G['d'].p1125_data[0]['datetime'], '%Y%m%d-%H%M%S')
    source_sel.data = {'t': [dt, dt], 'y': [PLOT_MIN, PLOT_MAX]}

    doc_layout.add_root(column(hdr1, hdr2, s, row(plot, plot_rt)))
    return True


main()
