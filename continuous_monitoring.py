#! /usr/bin/python2
from datetime import datetime
import time
import sys
import os
import RPi.GPIO as GPIO
from hx711 import HX711
from os.path import expanduser

def save(measurements, threshold = 1):
    basename = os.path.join(os.sep+'home', 'pi','weight_sensor',datetime.today().strftime('%Y-%m-%d_%H-%M'))
    i = 1
    file_name_to_use = basename + '_' + str(i) + '.log'
    while os.path.isfile(file_name_to_use):
        i += 1
        file_name_to_use = basename + '_' + str(i) + '.log'
    with open(file_name_to_use,"w") as fil:
        fil.write(f'date,time,threshold ({threshold}),weight\n')
        for line in measurements:
            fil.write(line[0].strftime('%Y-%m-%d') + ',' + line[0].strftime('%H-%M-$S') + f',{line[1]>threshold},{line[1]:4.2f}\n')

def measure(scale, times, sleepdur=0.1):
    vals = []
    for i in range(0, times):
        vals.append(hx.get_weight(5))
        time.sleep(sleepdur)
    return (sum(vals)/len(vals))/1000

def clean_exit():
    GPIO.cleanup()
    print('Clean exit.')
    sys.exit()

referenceUnit = -23
hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()

avg = 5
save_interval = 15
measurement_rest_time = 1
tare_every_n_min = 5
threshold = 1

last_save = datetime.now()
last_tare = datetime.now()
weights = []
while True:
    try:
        if (datetime.now()-last_tare).seconds > (60*tare_every_n_min):
            hx.reset()
            hx.tare()
        val = measure(hx,avg)
        if val > threshold:
            last_tare = datetime.now()
        weights.append([datetime.now(),val])
        if (weights[-1][0]-last_save).seconds >= (save_interval*60):
            save(weights, threshold)
            last_save = weights[-1][0]
            weights = []
        hx.power_down()
        hx.power_up()
        time.sleep(measurement_rest_time)
    except:
        clean_exit()
