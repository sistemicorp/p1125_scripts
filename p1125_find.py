#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2021 sistemicorp

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

See: https://pypi.org/project/zeroconf/

Example of finding the P1125 via avahi/bonjour service.
The info found is similar to,

    Service p1125-ba1c ._p1125._tcp.local. added,
        service info: ServiceInfo(type='_p1125._tcp.local.',
                                  name='p1125-ba1c ._p1125._tcp.local.',
                                  addresses=[b'\n\x00\x00\xcd'],
                                  port=80, weight=0, priority=0,
                                  server='p1125-ba1c.local.',
                                  properties={b'hostname': b'p1125-ba1c',
                                              b'sdcardver': b'14',
                                              b'image': b'p1125r',
                                              b'mac': b'dc:a6:32:3e:ba:1c',
                                              b'macwlan': b'aa:df:55:f4:ea:fb',
                                              b'date': b'Mon Dec  6 15:03:15 EST 2021'},
                                  interface_index=None)

From this service information, you can then extract the P1125 hostname,
p1125-ba1c.local, to either use in your browser, or in scripts to access it.
Note the IP address is shown above in 32bit format.

The P1125 avahi service is present BEFORE the P1125 application is running.
It is therefore required that you ping the P1125 to confirm that it is ready.
See p1125_example_ping.py

"""
from zeroconf import ServiceBrowser, Zeroconf


class MyListener:

    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print("Service %s added, service info: %s" % (name, info))

    def update_service(self, zeroconf, service_type, name):
        pass


zeroconf = Zeroconf()
listener = MyListener()
browser = ServiceBrowser(zeroconf, "_p1125._tcp.local.", listener)
try:
    input("Press enter to exit...\n\n")
finally:
    zeroconf.close()
