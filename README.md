# p1125_scripts
P1125 Python REST API scripts, demos and examples.

Instillation
------------
* Install Python 3.6 (or greater)
* Install your favorite Python IDE, for example PyCharm
* Clone this repo
* Install python requirements from `requirements.txt`


    $ pip3 install -r requirements.txt

Getting Started
---------------
* The REST API depends on knowing the IP address, or hostname of the P1125.
* All the example scripts have a section that looks like this,


```python
    # NOTE: Change to P1125 IP address or hostname
    P1125_URL = "http://IP_ADDRESS_OR_HOSTNAME/api/V1"
    
    if "IP_ADDRESS_OR_HOSTNAME" in P1125_URL:
        logger.error("Please set P1125_URL with valid IP/Hostname")
        exit(1)
```
        
* `IP_ADDRESS_OR_HOSTNAME` needs to be changed to reflect the P1125 IP address or hostname.
* The hostname of the P1125 is written on the bottom of the device, in the format `p1125-####`.
  * If you cannot connect to the P1125, the most sure way is to find the IP address, either by 
    accessing your router list of devices, or, connect a monitor/keyboard/mouse to the P1125,
    open a terminal, and type command `ifconfig` which will list the network interfaces and
    IP address being used.
  * once the IP address is found, change the example scripts, for example,
  
```python
    P1125_URL = "http://192.168.0.123/api/V1"
```
    
* The first script to try, to confirm everything is working is `python3 p1125_example_plot_cal_loads.py`

Plotting Results
----------------
The scripts use open source plotting framework `bokeh`, https://docs.bokeh.org/en/latest/index.html

Long Time Logging Script
------------------------
The (example) script `p1125_example_mahrs_logging.py` is provided as an example on how to take long time
 (hours, days, etc) measurement logs.  The companion script `p1125_example_mahrs_logging_plot.py` plots the data.
 
The measurement data for long time logs comes from the "mAhr" data stream of the P1125.  This stream is
averaged measurement data from the real time P1125 data acquisition path.  The P1125 sampling rate is always 31.25 kHz
(32usec samples).  The "mAhr" stream takes these samples and integrates them over a ~15ms window to determine
the average for that window.  Fast events within the ~15ms window are of course included in this average.
This averaging is done to reduce the amount of data to process when dealing with long time logs. In addition to this
averaging, the data is further reduced by getting rid of data that is within a small percentage of the previous
sample.  This reduction varies depending on the data pattern.

There are two main parameters to set up for a long term log,
* `TIME_CAPTURE_WINDOW_S`
  * This represents the total time to take ~15ms samples.
  * A resonable value for this is `60` (seconds).  This will result in up to ~4k samples per capture window.
* `TIME_TOTAL_RUN_S`
  * This sets the total run time.

These, and other, parameters are set at the top of the script,

```python
# Change these parameters to suit your needs:
VOUT = 1500                   # mV, output voltage, 1500-4500 mV
CONNECT_PROBE = False         # set to True to attach probe, !! Warning: check VOUT setting !!
TIME_CAPTURE_WINDOW_S = 60    # seconds over which to measure the AVERAGE mAhr
TIME_TOTAL_RUN_S = 300        # 3600 * 6   # seconds, total run time of the log
LOG_FILE_PATH = "./"          # path to output file, use USB stick if possible

WRITE_PLOT_DATA = True        # flag for write_data()
WAIT_POLLING_TIME_S = 0.5     # time to wait between polls whilst waiting for TIME_CAPTURE_WINDOW_S to complete
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
{'datetime': '20201116-135501', 'time_s': 63.24122, 'mAhr': 0.7496259, 'iavg_max_ua': 753.5487, 'samples': 40,'plot': {'t': [0, 5.640928, 5.654016, 5.667104, 5.680192, 5.69328, 5.706368, 5.745632, 5.75872, 5.771808, ...
{'datetime': '20201116-135605', 'time_s': 63.24122, 'mAhr': 0.7488481, 'iavg_max_ua': 751.5684, 'samples': 36,'plot': {'t': [0, 1.989376, 2.002464, 2.015552, 2.15952, 2.172608, 2.185696, 2.198784, 2.211872, 2.264224, ...
{'datetime': '20201116-135708', 'time_s': 63.24122, 'mAhr': 0.7486486, 'iavg_max_ua': 751.399, 'samples': 26,'plot': {'t': [0, 15.78413, 15.8103, 19.7367, 19.76288, 23.68928, 23.71546, 27.64186, 27.66803, 31.59443, ...
{'datetime': '20201116-135811', 'time_s': 63.24122, 'mAhr': 0.7484611, 'iavg_max_ua': 751.2046, 'samples': 26,'plot': {'t': [0, 15.78413, 15.8103, 19.7367, 19.76288, 23.68928, 23.71546, 27.64186, 27.66803, 31.59443, ...
{'datetime': '20201116-135915', 'time_s': 63.24122, 'mAhr': 0.748446, 'iavg_max_ua': 751.0996, 'samples': 26,'plot': {'t': [0, 15.78413, 15.8103, 19.7367, 19.76288, 23.68928, 23.71546, 27.64186, 27.66803, 31.59443,  ...
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
![alt text](https://github.com/sistemicorp/p1125_scripts/raw/master/readme_images/logging_plot.png "Logging Plot")

  