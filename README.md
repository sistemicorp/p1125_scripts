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
  

    P1125_URL = "http://192.168.0.123/api/V1"
    
* The first script to try, to confirm everything is working is `python3 p1125_example_plot_cal_loads.py`

Plotting Results
----------------
The scripts use open source plotting framework `bokeh`, https://docs.bokeh.org/en/latest/index.html

