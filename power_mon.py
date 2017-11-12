#!/usr/bin/env python
#
# The MIT License (MIT)
# Copyright (c) 2017 Michael E. O'Connor
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import signal
import sys
import time
import urllib2
from axp209 import AXP209

# Set to True for descriptive print statements, otherwise set to False

DEBUG = True

# Set sleep time valiables (nft = No Trouble Found, tf = Trouble Found)

ntf_sleep = 60
tf_sleep = 60

# Specify IFTTT supplied key from Webhooks. IFTTT account is required
# Obtain key from: https://ifttt.com/services/maker_webhooks/settings

maker_key = 'XXXXXXXXXXXXXXXXXXX'

# IFTTT function forms the required URL based on <EVENT-TYPE> corresponding to Applet Name

def ifttt_handler (event, type):
    maker_event = '%s-%s' % (event, type)
    url = 'https://maker.ifttt.com/trigger/%s/with/key/%s' % (maker_event, maker_key)
    f = urllib2.urlopen(url)
    response = f.read()
    f.close()
    return response


# Define a signal handler to enable clean break from while loop with CTRL-C (if running from shell)

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)


def main():

    signal.signal(signal.SIGINT, signal_handler)

    event = 'CHIP'                      # Indicate this is a 'CHIP' related event

    while True:

        axp = AXP209()			# Get CHIP power / temp stats

	if axp.battery_exists != True:
	    print("Warning - Battery Missing!")
	    sys.exit(1)

	if DEBUG: 
            print("internal_temperature: %.2fC" % axp.internal_temperature)
            print("battery_voltage: %.1fmV" % axp.battery_voltage)
            print("battery_current_direction: %s" % ("charging" if axp.battery_current_direction else "discharging"))
            print("battery_discharge_current: %.1fmA" % axp.battery_discharge_current)
            print("battery_charge_current: %.1fmA" % axp.battery_charge_current)
            print("battery_gauge: %d%%" % axp.battery_gauge)

	if (axp.internal_temperature >= 60.0):
	    type = "OVER_TEMP"
            response = ifttt_handler(event, type)
            if DEBUG:
                print("IFTTT Response: " + response)   		
	    sleeptime = tf_sleep

        if (axp.battery_current_direction == False) and (axp.battery_gauge <= 95):
            type = "LOST_POWER"
	    response = ifttt_handler(event, type)
	    if DEBUG: 
                print("IFTTT Response: " + response)   		
                print("battery_current_direction: %s" % ("charging" if axp.battery_current_direction else "discharging"))
                print("battery_gauge: %d%%" % axp.battery_gauge)
	    sleeptime = tf_sleep

	else:
	    if DEBUG:
	        print("No trouble found")
            sleeptime = ntf_sleep

        # Clean-up and wait before checking again

	axp.close()
	if DEBUG:
            print("Sleeping: %d seconds..." % sleeptime)
        time.sleep(sleeptime)		


# Standard boilerplate to call the main() function.

if __name__ == '__main__':
  main()
