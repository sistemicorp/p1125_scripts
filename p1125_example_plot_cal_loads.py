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
2) Change line 64 to suit your environment.
3) Chrome browser.

Notes:
1) Calibration loads are only attached to the supply when the probe is DISCONNECTED.

"""
from time import sleep
import numpy as np
import logging
from bokeh.layouts import layout, row
from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool, BoxZoomTool, ResetTool, UndoTool, PanTool, ZoomInTool

from P1125 import P1125, P1125API

logger = logging.getLogger()
logger.setLevel(logging.INFO)
FORMAT = "%(asctime)s: %(filename)32s: %(funcName)25s %(lineno)4s - %(levelname)-5.5s : %(message)s"
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

p1125 = P1125(url=URL, loggerIn=logger)

# bokeh plot setup
PLOT_WIDTH = 600
PLOT_HEIGHT = 800
plot = figure(toolbar_location="above", width=PLOT_WIDTH, height=PLOT_HEIGHT, y_range=(1, 2000000),
              y_axis_type="log", title="Current Min/Avg/Max/Expected vs VOUT")
plot.xaxis.axis_label = "VOUT (mV)"
plot.yaxis.axis_label = "Current (uA)"

plot_sigma = figure(toolbar_location="above", width=PLOT_WIDTH, height=PLOT_HEIGHT, y_range=(1, 2000000),
                    y_axis_type="log", title="RMS Noise (as % of Expected) vs VOUT")
plot_sigma.xaxis.axis_label = "VOUT (mV)"
plot_sigma.yaxis.axis_label = "Current (uA)"

plot_errp = figure(toolbar_location="above", width=PLOT_WIDTH, height=PLOT_HEIGHT, y_range=(1, 2000000),
                   y_axis_type="log", title="Peak Error (as % of Expected) vs VOUT")
plot_errp.xaxis.axis_label = "VOUT (mV)"
plot_errp.yaxis.axis_label = "Current (uA)"

doc_layout = layout()

data = {
    "vout": [],
    "min": [],
    "max": [],
    "avg": [],
    "exp": [],
    "err": [],
    "errp": [],  # peak error
    "res": [],
    "sigma": [],
    "sigma_percent": [],
}  # global dict to hold plotting vectors
source = ColumnDataSource(data=data)

VOUT = [1800, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000, 7500, 8000]
#VOUT = [4000]  # for debugging

SPAN = P1125API.TBASE_SPAN_500MS
PLOT_CIRCLE_ERR = 10          # percent error as "green circle" reference on the plots
CURRENT_MIN_UA  = 1.0         # skip setups where the expected current is less than CURRENT_MIN_UA

# WARNING! Do not exceed 900mA or damage may occur!
CURRENT_MAX_UA  = 900000.0    # skip setups where the expected current is more than CURRENT_MAX_UA

#                   loads to cycle thru         Resistance
LOADS_TO_PLOT = [([P1125API.DEMO_CAL_LOAD_2M],  2000000.0),
                 ([P1125API.DEMO_CAL_LOAD_200K], 200000.0),
                 ([P1125API.DEMO_CAL_LOAD_20K],   20000.0),
                 ([P1125API.DEMO_CAL_LOAD_2K],     2000.0),
                 ([P1125API.DEMO_CAL_LOAD_200],     200.0),
                 ([P1125API.DEMO_CAL_LOAD_20],       20.0),
                 ([P1125API.DEMO_CAL_LOAD_8],         8.06),
                 ]


def main():
    """
    An example sequence of commands to make a measurement with the P1125 REST API.

    The internal Calibration loads will be used to plot essentially DC currents of various magnitudes.
    Since internal loads are used, the Probe is not connected.
    """

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

    success, result = p1125.set_timebase(SPAN)
    logger.info("set_timebase: {}".format(result))
    if not success: return False

    success, result = p1125.set_trigger(src=P1125API.TRIG_SRC_NONE,
                                        pos=P1125API.TRIG_POS_LEFT,
                                        slope=P1125API.TRIG_SLOPE_RISE,
                                        level=1.0)
    logger.info("set_trigger: {}".format(result))
    if not success: return False

    for vout in VOUT:

        success, result = p1125.set_vout(vout)
        logger.info("set_vout: {}".format(result))
        if not success: return False

        for load, resistance in LOADS_TO_PLOT:
            expected_i_ua = float(vout) / resistance * 1000.0
            if expected_i_ua < CURRENT_MIN_UA or expected_i_ua > CURRENT_MAX_UA:
                logger.info("SKIP (Current out of range): {} mV, {:0.3f} Ohms, expected {:.1f} uA".format(vout, resistance, expected_i_ua))
                continue

            logger.info("{} mV, {}, expected {} uA".format(vout, resistance, expected_i_ua))

            success, result = p1125.set_cal_load(loads=load)
            logger.info("set_cal_load: {}".format(result))
            if not success: break

            success, result = p1125.acquisition_start(mode=P1125API.ACQUIRE_MODE_SINGLE)
            logger.info("acquisition_start: {}".format(result))
            if not success: break

            success, result = p1125.acquisition_complete()
            logger.info("acquisition_complete: {}".format(result))
            if not success: break

            p1125.set_cal_load(loads=[P1125API.DEMO_CAL_LOAD_NONE])
            p1125.acquisition_stop()

            _, result = p1125.acquisition_get_data()

            samples = len(result["i"])
            data["vout"].append(vout)
            data["min"].append(min(result["i"]))
            data["max"].append(max(result["i"]))
            data["avg"].append(sum(result["i"]) / samples)
            data["exp"].append(expected_i_ua)
            data["err"].append((abs(data["avg"][-1] - data["exp"][-1]) * 100.0) / data["exp"][-1])
            data["res"].append(resistance)

            # find the peak error from the acquistion
            peak_error = max(abs(data["exp"][-1] - data["min"][-1]), abs(data["exp"][-1] - data["max"][-1]))
            data["errp"].append(peak_error * 100.0 / data["exp"][-1])

            sigma = np.std(result["i"])
            data["sigma"].append(sigma)
            sigma_as_percent = sigma * 100.0 / data["exp"][-1]
            data["sigma_percent"].append(sigma_as_percent)
            logger.info("""VOUT {} mV, Expected {:9.2f} uA, min/avg/max: {:9.2f} {:9.2f} {:9.2f} uA, sigma {:8.3f} ({:3.1}%), {} samples""".format(data["vout"][-1],
                                                                                            data["exp"][-1],
                                                                                            data["min"][-1],
                                                                                            data["avg"][-1],
                                                                                            data["max"][-1],
                                                                                            sigma, sigma_as_percent,
                                                                                            samples
                                                                                            ))
            # large error...
            #if data["errp"][-1] > PLOT_CIRCLE_ERR: logger.error(result["i"])

    plot.cross(x="vout", y="avg", size=10, color="blue", source=source)
    plot.dot(x="vout", y="exp", size=20, color="olive", source=source)
    plot.dash(x="vout", y="min", size=10, color="red", source=source)
    plot.dash(x="vout", y="max", size=10, color="red", source=source)

    _tooltips_sigma = [("Sigma", "@sigma_percent{0.0} %"), ]
    dotssigma = plot_sigma.circle_dot(x="vout", y="exp", size="sigma_percent", fill_alpha=0.2, line_width=1, color="red", source=source)
    plot_sigma.circle(x="vout", y="exp", size=PLOT_CIRCLE_ERR, fill_alpha=0.2, line_width=0, color="green", source=source)
    htsigma = HoverTool(tooltips=_tooltips_sigma, mode='vline', show_arrow=True, renderers=[dotssigma])
    plot_sigma.tools = [htsigma, BoxZoomTool(), ZoomInTool(), ResetTool(), UndoTool(), PanTool()]

    _tooltips_peak = [("Error", "@errp{0.0} %"), ]
    dotsp = plot_errp.circle_dot(x="vout", y="exp", size="errp", fill_alpha=0.2, color="red", source=source)
    plot_errp.circle(x="vout", y="exp", size=PLOT_CIRCLE_ERR, fill_alpha=0.2, line_width=0, color="green", source=source)
    htp = HoverTool(tooltips=_tooltips_peak, mode='vline', show_arrow=True, renderers=[dotsp])
    plot_errp.tools = [htp, BoxZoomTool(), ZoomInTool(), ResetTool(), UndoTool(), PanTool()]

    doc_layout.children.append(row(plot, plot_errp, plot_sigma))
    show(doc_layout)
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
