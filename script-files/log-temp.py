#!/usr/bin/python3

from time import sleep
import pyodbc, sys, os, logging
from logging.handlers import TimedRotatingFileHandler

## VARIABLES
basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
sensor_id = 1 #SENSOR ID: 1=EGG COOLER / 2=DOUGH COOLER
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
temp_sensor = '/sys/bus/w1/devices/28-02159245de3b/w1_slave'

## LOGGING
logHandler = TimedRotatingFileHandler('{}/../logs/log-temp.log'.format(basepath), when='midnight', backupCount=7)
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logHandler.setFormatter(logFormatter)
log = logging.getLogger("log-temp")
log.setLevel(logging.DEBUG)
log.addHandler(logHandler)

## RETRIEVE RAW DATA
def temp_raw():
    f = open(temp_sensor, 'r')
    lines = f.readlines()
    return lines

## FORMAT
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

## WRITE TO DB
def write_temp(write_value):
    try:
        cnxn = pyodbc.connect('DRIVER={FreeTDS};SERVER=xxxxx.xxxxx.com;PORT=1433;DATABASE=xxxxx;UID=xxxxx;PWD=xxxxx;TDS_VERSION=7.2')
        cursor = cnxn.cursor()
        cursor.execute("INSERT INTO tbl_coolers (probe_date, probe_sensor_id, probe_type_id, probe_value) OUTPUT INSERTED.id VALUES(CURRENT_TIMESTAMP, ?, ?, ?)", (sensor_id, 1, write_value))
        cnxn.commit()
        cnxn.close()
    except pyodbc.Error:
        log.warning("Failed to write record to database, {}".format(sys.exc_info()[0]))
    else:
        log.debug("Log success")

## MAIN
write_temp(temp_read())
