#!/usr/bin/python3

import sys, os, json
from time import sleep
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
recipients_file = '{}/../resource-files/recipients.json'.format(basepath)
with open( recipients_file, 'r' ) as rargs:
    addr_list = json.load(rargs)
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
temp_sensor = '/sys/bus/w1/devices/28-02159245de3b/w1_slave'

def temp_raw():
    f = open(temp_sensor, 'r')
    lines = f.readlines()
    return lines

def temp_read():
    lines = temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = temp_raw()
    temp_out = lines[1].find('t=')
    if temp_out != -1:
        temp_string = lines[1].strip()[temp_out+2:]
        temp_c = float( temp_string ) / 1000.0
        temp_f = float( "{0:.2f}".format( temp_c * 9.0 / 5.0 + 32.0 ) )
        return temp_f

app = Flask(__name__)

@app.route("/temperature/", methods=['GET', 'POST'])
def incoming():
    """Respond to incoming messages with a friendly SMS."""
    # Start our response
    resp = MessagingResponse()

    # Retreive incoming message
    body = request.values.get('Body', None)
    from_num = request.values.get('From', None)
    from_name = next( ( item for item in addr_list if item['phone_number'] == from_num), None)
    if from_name:
        from_name = from_name['name'].split(', ')[1]

    # Respond
    if body == 'temp':
        resp.message("{}, current is {}F".format(from_name,temp_read()))
    #elif :
    #    resp.message("Empty set")
    
    return str(resp)
