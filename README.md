# P1125 Online Help

[P1125 Online Help](https://sistemicorp.github.io/p1125_scripts/html/index.html)

# p1125_scripts
The P1125 can be automated using its JSON-RPC interface.  This repo shows Python
examples of the JSON-RPC API.

The example scripts use a Python class in `P1125.py` that makes it easy to use the JSON-RPC
API, as if the API were just typical Python class function calls.

Instillation
------------
* Install Python 3.6 (or greater)
* Install your favorite Python IDE, for example PyCharm
* Clone this repo
* Install python requirements from `requirements.txt`

  ```bash
  pip3 install -r requirements.txt
  ```


Getting Started
---------------
* The JSON_RPC API requires the IP address, or hostname of the P1125.
* All the example scripts have a section that looks like this,


```python
    # NOTE: Change to P1125 IP address or hostname
    P1125_URL = "p1125-####.local"  # for example, p1125-a12b.local, or 192.168.0.123
    
    if "p1125-####.local" in P1125_URL:
        logger.error("Please set P1125_URL with valid IP/Hostname")
        exit(1)
```
        
* `p115-####.local` needs to be changed to reflect the P1125 IP address or hostname of your device.
* The hostname of the P1125 is written on the bottom of the device, in the format `p1125-####.local`.
* Or if the IP address is known, that may be used.
  
```python
    P1125_URL = "192.168.0.123"
```

* Testing your P1125 connection
  * Start with the `p1125_example_ping.py` script.  This script will simply ping your P1125.
  * Update `P1125_URL` as described above.
  * Example output,  

        /usr/bin/python3.6 /home/martin/git/p1125_scripts/p1125_example_ping.py
        2021-07-19 13:05:56,688:       ping  217 - INFO  : V1.ping http://192.168.86.24:6590/api/V1
        2021-07-19 13:05:56,712:       main   73 - INFO  : {'success': True, 'version': 'Ver0.4-31', 'rpi_serial': '1000000062fc4808', 'url': 'p1125-419b', 'a10_serial': '2e0052000d50533742393220', 'a10_hw_ver': 2686519040, 'a10_bom': 4294967295, 'mac_eth0': 'dc:a6:32:6a:41:9b', 'mac_wlan0': 'dc:a6:32:6a:41:9c'}
        2021-07-19 13:05:56,712:     status  222 - INFO  : V1.status
        2021-07-19 13:05:56,727:       main   77 - INFO  : {'success': True, 'version': 'Ver0.4-31', 'cal_done': False, 'aqc_in_progress': False, 'temperature_degc': 34, 'error': [], 'error_action': []}
        
        Process finished with exit code 0
    
  * This confirms you can access the P1125 remotely.

* You may then try the other scripts, and/or copy one of them and modify for your use.
  * `python3 p1125_example_plot_cal_loads.py`
    * Example of how to pull real time plot data.
    * The example uses the internal CAL loads, but can be modified to use target data.  
  * `p1125_example_mahrs.py`
    * Script that plots the mAhrs versus VOUT.
    * This example shows how your target current changes with Battery voltage.  Battery
      voltage changes as the battery is drained, and the efficiency of your target buck/boost
      converters will change with changing input voltage.

Plotting Results
----------------
The scripts use open source plotting framework `bokeh`, https://docs.bokeh.org/en/latest/index.html

Long Time Logging Script
------------------------
The (example) script `p1125_example_mahrs_logging.py` is provided as an example on how to take long time
 (hours, days, etc) measurement logs.  The companion script `p1125_example_mahrs_logging_plot.py` plots the data.
 
The measurement data for long time logs comes from the "mAhr" data stream of the P1125.  This stream is
averaged measurement data from the real time P1125 data acquisition path.  The P1125 sampling rate is always 48kHz
(20.83 usec).  The "mAhr" stream takes these samples and integrates them over a 10ms window (480 samples) to determine
the average for that window.  Fast events within the 10ms window are of course included in this average Because the
sample rate is maintained at 48KHz. This averaging is done to reduce the amount of data to process when dealing
with long time plots/logs.  Also, the peak current within the 10ms window is also recorded and is plotted in
the example script.

There are two main parameters to set up for a long term log,
* `TIME_CAPTURE_WINDOW_S`
  * This represents the total time to take 10ms samples.
  * A resonable value for this is `60` (seconds).  This will result in up to ~4k samples per capture window.
* `TIME_TOTAL_RUN_S`
  * This sets the total run time.

These, and other, parameters are set at the top of the script,

```python
# Change these parameters to suit your needs:
VOUT = 3000                   # mV, output voltage, 1800-4500 mV
CONNECT_PROBE = False         # set to True to attach probe, !! Warning: check VOUT setting !!
TIME_CAPTURE_WINDOW_S = 60    # seconds over which to measure the AVERAGE mAhr
TIME_TOTAL_RUN_S = TIME_CAPTURE_WINDOW_S * 5   # seconds, total run time of the log
LOG_FILE_PATH = "./"          # path to output file (filename is generated)
```

The logging script will generate a python file with the measurement data.  This log file name is a date stamp.
An example of such a file is shown here,

```python
# This file is auto-generated by p1125_example_mahrs_logging.py                                                                                                                                                            
# 20201116-135355.py                                                                                                                                                                                                   
p1125_ping = {'success': True, 'version': 'Ver0.3-250', 'rpi_serial': '1000000062fc4808', 'url': 'p1125-419b', 'a10_serial': '390032000e504e4856333420', 'a10_hw_ver': 2685408000, 'a10_bom': 4294967295}              
p1125_status = {'success': True, 'version': 'Ver0.3-250', 'cal_done': True, 'aqc_in_progress': False, 'temperature_degc': 25, 'error': [], 'error_action': []}                                                         
p1125_settings = {'VOUT': 1500, 'TIME_CAPTURE_WINDOW_S': 60, 'TIME_TOTAL_RUN_S': 300, 'CONNECT_PROBE': False}                                                                                                          
# NOTE: Might have to add missing last ']' if program was interrupted                                                                                                                                                  
p1125_data = [                                                                                                                                                                                                         
{'datetime': '20201116-135501', 'time_s': 63.24122, 'mAhr': 0.7496259, 'samples': 40,'plot': {'t': [0, 5.640928, 5.654016, 5.667104, 5.680192, 5.69328, 5.706368, 5.745632, 5.75872, 5.771808, ...
{'datetime': '20201116-135605', 'time_s': 63.24122, 'mAhr': 0.7488481, 'samples': 36,'plot': {'t': [0, 1.989376, 2.002464, 2.015552, 2.15952, 2.172608, 2.185696, 2.198784, 2.211872, 2.264224, ...
{'datetime': '20201116-135708', 'time_s': 63.24122, 'mAhr': 0.7486486, 'samples': 26,'plot': {'t': [0, 15.78413, 15.8103, 19.7367, 19.76288, 23.68928, 23.71546, 27.64186, 27.66803, 31.59443, ...
{'datetime': '20201116-135811', 'time_s': 63.24122, 'mAhr': 0.7484611, 'samples': 26,'plot': {'t': [0, 15.78413, 15.8103, 19.7367, 19.76288, 23.68928, 23.71546, 27.64186, 27.66803, 31.59443, ...
{'datetime': '20201116-135915', 'time_s': 63.24122, 'mAhr': 0.748446, 'samples': 26,'plot': {'t': [0, 15.78413, 15.8103, 19.7367, 19.76288, 23.68928, 23.71546, 27.64186, 27.66803, 31.59443,  ...
]                                                                                                                                                                                                                                                                                                                                                                                                                                             
```
The example script sets up a 2K Ohm load at 3000mV VOUT, so the expected current is ~750uA.  Because this test load is constant, there
isn't much interesting to see, and note the number of samples is greatly reduced because the load was static.

The plotting tool is executed thru the `bokeh server` because it is an interactive tool.  The plotting script is executed in this way,
from a command prompt,

```bash
$ bokeh serve --show p1125_example_mahrs_logging_plot.py --args -f 20201116-135355.py
```
Where the logging filename, `2020116-135355.py` will be specific to you.

Your browser should open similar to this,
![alt text](https://github.com/sistemicorp/p1125_scripts/raw/main/readme_images/logging_plot.png "Logging Plot")


