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

A command line tool for testing and/or using the P1125 REST API.

Typical sequence of commands,

    $python3 p1125_cli.py ping
    $python3 p1125_cli.py status
    $python3 p1125_cli.py cal --start
    $python3 p1125_cli.py cal --progress        # continue only if cal is done
    $python3 p1125_cli.py timebase --span TBASE_SPAN_100MS
    $python3 p1125_cli.py trig --source TRIG_SRC_NONE --position TRIG_POS_CENTER --slope TRIG_SLOPE_EITHER --level 1
    $python3 p1125_cli.py vout --set 4000
    $python3 p1125_cli.py probe --status
    $python3 p1125_cli.py probe --connect
    $python3 p1125_cli.py acquire --start
    $python3 p1125_cli.py acquire --triggered   # continue only if triggered
    $python3 p1125_cli.py probe --disconnect
    $python3 p1125_cli.py plot_data

Help is available,

    $python3 p1125_cli.py --help
    $python3 p1125_cli.py cal --help
    $python3 p1125_cli.py trig --help
    ...

"""
import requests
import argparse
import logging

from p1125api import P1125API

logger = logging.getLogger()
logger.setLevel(logging.INFO)
FORMAT = "%(asctime)s: %(funcName)20s %(lineno)4s - %(levelname)-5.5s : %(message)s"
formatter = logging.Formatter(FORMAT)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

# NOTE: Change to P1125 IP address or hostname
P1125_URL = "http://IP_ADDRESS_OR_HOSTNAME/api/V1"

if "IP_ADDRESS_OR_HOSTNAME" in P1125_URL:
    logger.error("Please set P1125_URL with valid IP/Hostname")
    exit(1)


def _log_response(response):
    if "error" in response:
        logger.error(response['error'])
        return False

    logger.info(response["result"])
    return True


def ping(args):
    payload = {"method": "V1.ping", "jsonrpc": "2.0", "id": 0,}
    response = requests.post(P1125_URL, json=payload).json()
    return _log_response(response)


def status(args):
    payload = {"method": "V1.status", "jsonrpc": "2.0", "id": 0,}
    response = requests.post(P1125_URL, json=payload).json()
    return _log_response(response)


def cal(args):

    if args._start:
        payload = {"method": "V1.cal", "jsonrpc": "2.0", "id": 0, }
        response = requests.post(P1125_URL, json=payload).json()
        return _log_response(response)

    elif args._status:
        payload = {"method": "V1.cal_status", "jsonrpc": "2.0", "id": 0, }
        response = requests.post(P1125_URL, json=payload).json()
        return _log_response(response)

    elif args._values:
        payload = {"method": "V1.cal_values", "jsonrpc": "2.0", "id": 0, }
        response = requests.post(P1125_URL, json=payload).json()
        return _log_response(response)

    else:
        logger.error("unknown argument: {}".format(args))


def vout(args):
    if args._set:
        payload = {"method": "V1.vout", "jsonrpc": "2.0", "id": 0,
                   "params": {"value": args._set}}
        response = requests.post(P1125_URL, json=payload).json()
        return _log_response(response)


def probe(args):
    if args._status:
        payload = {"method": "V1.probe_status", "jsonrpc": "2.0", "id": 0,}
        response = requests.post(P1125_URL, json=payload).json()
        return _log_response(response)

    elif args._connect:
        payload = {"method": "V1.probe_connect", "jsonrpc": "2.0", "id": 0,
                   "params": {"value": True}}
        response = requests.post(P1125_URL, json=payload).json()
        return _log_response(response)

    elif args._disconnect:
        payload = {"method": "V1.probe_connect", "jsonrpc": "2.0", "id": 0,
                   "params": {"value": False}}
        response = requests.post(P1125_URL, json=payload).json()
        return _log_response(response)


def trig(args):
    payload = {"method": "V1.trigger", "jsonrpc": "2.0", "id": 0,
               "params": {"source": args._source,
                          "position": args._position,
                          "slope": args._slope,
                          "level": float(args._level)}
               }
    response = requests.post(P1125_URL, json=payload).json()
    return _log_response(response)


def acquire(args):
    if args._start:
        payload = {"method": "V1.acquire_start", "jsonrpc": "2.0", "id": 0,}
        response = requests.post(P1125_URL, json=payload).json()
        return _log_response(response)

    elif args._stop:
        payload = {"method": "V1.acquire_stop", "jsonrpc": "2.0", "id": 0,}
        response = requests.post(P1125_URL, json=payload).json()
        return _log_response(response)

    elif args._triggered:
        payload = {"method": "V1.acquire_is_triggered", "jsonrpc": "2.0", "id": 0,}
        response = requests.post(P1125_URL, json=payload).json()
        return _log_response(response)


def plotdata(args):
    payload = {"method": "V1.plot_data", "jsonrpc": "2.0", "id": 0,}
    response = requests.post(P1125_URL, json=payload).json()
    return _log_response(response)


def timebase(args):
    if args._span:
        payload = {"method": "V1.timebase", "jsonrpc": "2.0", "id": 0,
                   "params": {"span": args._span,}
                  }
        response = requests.post(P1125_URL, json=payload).json()
        return _log_response(response)


def calload(args):
    if args._load:
        loads = args._load.split(',')
        payload = {"method": "V1.cal_load", "jsonrpc": "2.0", "id": 0,
                   "params": {"loads": loads}}
        response = requests.post(P1125_URL, json=payload).json()
        return _log_response(response)


if __name__ == "__main__":
    epilog = """
    Usage examples:
       python3 test_rpc.py [OPTIONS] ping

    """
    parser = argparse.ArgumentParser(description='p1125r rpc CLI',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=epilog)

    parser.add_argument("-v", '--verbose', dest='verbose', default=0, action='count', help='Increase verbosity')
    parser.add_argument("-d", '--debug', dest='debug', default=False, action='store_true', help='Enable debug prints on pyboard')
    parser.add_argument("--version", dest="show_version", action='store_true', help='Show version and exit')

    subp = parser.add_subparsers(dest="_cmd", help='commands')

    ping_parser = subp.add_parser('ping')

    status_parser = subp.add_parser('status')

    cal_parser = subp.add_parser('cal')
    cal_parser.add_argument('-s', '--start',    dest="_start",   help='calibration start',  action='store_true')
    cal_parser.add_argument('-p', '--progress', dest="_status",  help='calibration status', action='store_true')
    cal_parser.add_argument('-v', '--values',   dest="_values",  help='calibration values', action='store_true')

    vout_parser = subp.add_parser('vout')
    vout_parser.add_argument('-s', '--set',    dest="_set",   help='vout set <value>, where value 1500-4500 (mV)',  action='store')

    probe_parser = subp.add_parser('probe')
    probe_parser.add_argument('-s', '--status',     dest="_status",   help='probe status',  action='store_true')
    probe_parser.add_argument('-c', '--connect',    dest="_connect",  help='probe connect',  action='store_true')
    probe_parser.add_argument('-d', '--disconnect', dest="_disconnect",  help='probe disconnect',  action='store_true')

    trig_parser = subp.add_parser('trig')
    trig_parser.add_argument('-s', '--source',    dest="_source", required=True,
                             help='trigger source, one of {}'.format(P1125API.TRIG_SRC_LIST),
                             choices=P1125API.TRIG_SRC_LIST,
                             action='store')
    trig_parser.add_argument('-p', '--position',  dest="_position", required=True,
                             help='trigger position, one of {}'.format(P1125API.TRIG_POS_LIST),
                             choices=P1125API.TRIG_POS_LIST,
                             action='store')
    trig_parser.add_argument('-e', '--slope',     dest="_slope", required=True,
                             help='trigger slope, one of {}'.format(P1125API.TRIG_SLOPE_LIST),
                             choices=P1125API.TRIG_SLOPE_LIST,
                             action='store')
    trig_parser.add_argument('-l', '--level',     dest="_level", required=True,
                             help='trigger level, in uA or mV',
                             action='store')

    acquire_parser = subp.add_parser('acquire')
    acquire_parser.add_argument('-s', '--start',     dest="_start",     help='acquire start', action='store_true')
    acquire_parser.add_argument('-t', '--triggered', dest="_triggered", help='acquire check triggered', action='store_true')
    acquire_parser.add_argument('-f', '--stop',      dest="_stop",      help='acquire stop',  action='store_true')

    plotdata_parser = subp.add_parser('plot_data')

    tbase_parser = subp.add_parser('timebase')
    tbase_parser.add_argument('-s', '--span',     dest="_span",
                              help='timebase span',
                              choices=P1125API.TBASE_SPAN_LIST,
                              action='store')

    calload_parser = subp.add_parser('cal_load')
    calload_parser.add_argument('-l', '--load', dest="_load",
                                help='calibration load set, comma separated list of {}'.format(P1125API.DEMO_CAL_LOAD_LIST),
                                action='store')

    args = parser.parse_args()

    if args.verbose > 0:
        logger.setLevel(logging.DEBUG)

    if args._cmd is not None:
        logger.debug(parser)

    if args._cmd == 'ping':
        success = ping(args)

    elif args._cmd == 'status':
        success = status(args)

    elif args._cmd == 'cal':
        success = cal(args)

    elif args._cmd == 'vout':
        success = vout(args)

    elif args._cmd == 'probe':
        success = probe(args)

    elif args._cmd == 'trig':
        success = trig(args)

    elif args._cmd == 'acquire':
        success = acquire(args)

    elif args._cmd == 'plot_data':
        success = plotdata(args)

    elif args._cmd == 'timebase':
        success = timebase(args)

    elif args._cmd == 'cal_load':
        success = calload(args)

    elif args._cmd in ['help']:
        parser.print_help()
