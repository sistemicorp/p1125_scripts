#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2020-2021 sistemicorp

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
    $python3 p1125_example_ping.py

Requirements:
1) Python 3.6+ and bokeh 2.2.0 (pip3 install bokeh) or greater installed.
2) Change line 61 to suit your environment.
3) Chrome browser.

--- !!! WARNING !!! ---
if CONNECT_PROBE is True, this example connects the PROBE at 3000 (VOUT) mV

"""
import logging
from P1125 import P1125, P1125API

logger = logging.getLogger()
logger.setLevel(logging.INFO)
FORMAT = "%(asctime)s: %(funcName)10s %(lineno)4s - %(levelname)-5.5s : %(message)s"
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

    return True


if __name__ == "__main__":
    success = main()
    if not success: logger.error("failed")
