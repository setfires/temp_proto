#!/usr/bin/python3

import pyodbc
from twilio.rest import Client
import json, os, sys, logging
from logging.handlers import TimedRotatingFileHandler
import sqlite3
from sqlite3 import Error

## VARIABLES
basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
limitval = 41
cooler = "egg"
last_alert_file = '{}/../resource-files/1.db'.format(basepath)
recipients_file = '{}/../resource-files/recipients.json'.format(basepath)
twilio_file = '{}/../resource-files/twilio.json'.format(basepath)
with open( twilio_file, 'r' ) as targs:
    twilio_args = json.load(targs)
with open( recipients_file, 'r' ) as rargs:
    addr_list = json.load(rargs)

## LOGGING
logHandler = TimedRotatingFileHandler('{}/../logs/log-notify.log'.format(basepath), when='midnight', backupCount=7)
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logHandler.setFormatter(logFormatter)
log = logging.getLogger("notify-temp")
log.setLevel(logging.DEBUG)
log.addHandler(logHandler)

## SMS
def send_message(val1,val2):
    for recipient in addr_list:
        # CREATE SMS API CALL - SEND MESSAGE
        try:
            client = Client(twilio_args[0]["sid"], twilio_args[0]["auth"])
            message = client.messages \
                .create(
                    body="{}, threshold {}F in {} cooler alert. Last two samples {}F and {}F".format(recipient["name"].split(', ')[1],limitval,cooler,val1,val2),
                    from_=twilio_args[0]["number"],
                    to=recipient["phone_number"]
                )
            log.debug("{} sent to {}".format(message.sid,recipient["name"]))
        except:
            log.warning("SMS alert failure, {}".format(sys.exc_info()[0]))

## Check last sent value
def last_alert(action):
    conn = None
    conn = sqlite3.connect(last_alert_file)
    c = conn.cursor()
    if action == "get":
        c.execute("SELECT sent FROM last_alert")
        c_state = c.fetchone()[0]
        return c_state
    else:
        c.execute('UPDATE last_alert SET sent = ? where id = 1', (action,))
        conn.commit()
    conn.close()

## MAIN
try:
    cnxn = pyodbc.connect('DRIVER={FreeTDS};SERVER=xxxxx.xxxxx.com;PORT=1433;DATABASE=xxxxx;UID=xxxxx;PWD=xxxxx;TDS_VERSION=7.2')
    cursor = cnxn.cursor()
    cursor.execute("SELECT TOP(2) tbl_coolers.probe_value AS PVAL FROM tbl_coolers WHERE probe_type_id = 1 AND probe_sensor_id = 1 ORDER BY tbl_coolers.probe_date DESC")
    rows = cursor.fetchall()
    cnxn.close()
    if rows[0].PVAL >= limitval and rows[1].PVAL >= limitval and last_alert("get") == "False":
        log.debug("Out of range -> Alert")
        send_message(rows[0].PVAL,rows[1].PVAL)
        last_alert("True")
    elif rows[0].PVAL <= limitval and rows[1].PVAL <= limitval:
        log.debug("In range")
        last_alert("False")
    else:
        log.debug("Out of range -> Repeat alert")

except pyobdc.Error:
    log.warning("Failed to read from database, {}".format(sys.exc_info()[0]))
else:
    log.debug("Check success")
