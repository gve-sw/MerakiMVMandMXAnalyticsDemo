# monitors for motion trigger from Meraki Camera MV Sense and writes it to a .txt file

import json, requests
import time
import paho.mqtt.client as mqtt
import csv
from config import MQTT_SERVER,MQTT_PORT,MQTT_TOPIC,MERAKI_API_KEY,NETWORK_ID,COLLECT_CAMERAS_SERIAL_NUMBERS,COLLECT_ZONE_IDS,MOTION_ALERT_PEOPLE_COUNT_THRESHOLD,MOTION_ALERT_ITERATE_COUNT,MOTION_ALERT_TRIGGER_PEOPLE_COUNT,MOTION_ALERT_PAUSE_TIME,TIMEOUT


_MONITORING_TRIGGERED = False

_MONITORING_MESSAGE_COUNT = 0

_MONITORING_PEOPLE_TOTAL_COUNT = 0

_TIMESTAMP = 0

_TIMEOUT_COUNT = 0



def collect_zone_information(topic, payload):
    ## /merakimv/Q2GV-S7PZ-FGBK/123

    parameters = topic.split("/")
    serial_number = parameters[2]
    zone_id = parameters[3]
    index = len([i for i, x in enumerate(COLLECT_ZONE_IDS) if x == zone_id])
    # if not wildcard or not in the zone_id list or equal to 0 (whole camera)
    if COLLECT_ZONE_IDS[0] != "*":
        if index == 0 or zone_id == "0":
            return

    # detect motion

    global _MONITORING_TRIGGERED, _MONITORING_MESSAGE_COUNT, _MONITORING_PEOPLE_TOTAL_COUNT, _TIMESTAMP, TIMEOUT, _TIMEOUT_COUNT

    # if motion monitoring triggered
    if _MONITORING_TRIGGERED:

        _MONITORING_MESSAGE_COUNT = _MONITORING_MESSAGE_COUNT + 1

        if _MONITORING_PEOPLE_TOTAL_COUNT < payload['counts']['person']:
            _MONITORING_PEOPLE_TOTAL_COUNT = payload['counts']['person']

        if payload['counts']['person'] > 0:
            _TIMEOUT_COUNT = 0
        elif payload['counts']['person'] == 0:
            _TIMEOUT_COUNT = _TIMEOUT_COUNT + 1

# Enough time has elapsed without action and the minimum number of Motion messages have been received to qualify for successful action
        if _TIMEOUT_COUNT >= TIMEOUT and _MONITORING_MESSAGE_COUNT >= MOTION_ALERT_ITERATE_COUNT:

# Minimum people count reached
            if _MONITORING_PEOPLE_TOTAL_COUNT >= MOTION_ALERT_TRIGGER_PEOPLE_COUNT:
                # notification
                print('---MESSAGE ALERT---' + serial_number, _MONITORING_PEOPLE_TOTAL_COUNT,_TIMESTAMP,payload['ts'])
                notify(serial_number, _MONITORING_PEOPLE_TOTAL_COUNT,_TIMESTAMP, payload['ts'])
                print('---ALERTED---')
                # pause
                time.sleep(MOTION_ALERT_PAUSE_TIME)

            # reset
            _MONITORING_MESSAGE_COUNT = 0

            _MONITORING_PEOPLE_TOTAL_COUNT = 0

            _MONITORING_TRIGGERED = False

            _TIMESTAMP = 0

            _TIMEOUT_COUNT = 0

        # not a registered action
        elif _TIMEOUT_COUNT >= TIMEOUT and _MONITORING_MESSAGE_COUNT < MOTION_ALERT_ITERATE_COUNT:
            # reset
            print('---ALERT DISMISSED---')
            _MONITORING_MESSAGE_COUNT = 0

            _MONITORING_PEOPLE_TOTAL_COUNT = 0

            _MONITORING_TRIGGERED = False

            _TIMESTAMP = 0

            _TIMEOUT_COUNT = 0


    # print(payload['counts']['person'])
    if payload['counts']['person'] >= MOTION_ALERT_PEOPLE_COUNT_THRESHOLD:
        _MONITORING_TRIGGERED = True
        _TIMESTAMP = payload['ts']
    print("payload "+serial_number+": " + str(payload) +
          ", _MONITORING_TRIGGERED : " + str(_MONITORING_TRIGGERED) +
          ", _MONITORING_MESSAGE_COUNT : " + str(_MONITORING_MESSAGE_COUNT) +
          ", _MONITORING_PEOPLE_TOTAL_COUNT : " + str(_MONITORING_PEOPLE_TOTAL_COUNT)+
          ", timeout: "+str(_TIMEOUT_COUNT))


def notify(serial_number,count,timestampIN, timestampOUT):
    with open('mvData.csv','a') as csvfile:
        fieldnames = ['Time In','Time Out','Count']
        writer=csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writerow({'Time In':timestampIN,'Time Out':timestampOUT, 'Count':count})


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    client.subscribe(MQTT_TOPIC)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode("utf-8"))
    parameters = msg.topic.split("/")
    serial_number = parameters[2]
    message_type = parameters[3]
    index = len([i for i, x in enumerate(COLLECT_CAMERAS_SERIAL_NUMBERS) if x == serial_number])


    # filter camera
    if COLLECT_CAMERAS_SERIAL_NUMBERS[0] != "*":
        if index == 0:
            return

    # if message_type != 'raw_detections' and message_type != 'light':
    #     print(message_type)
    #     collect_zone_information(msg.topic, payload)
    if message_type == '0':
        collect_zone_information(msg.topic,payload)


if __name__ == "__main__":

    # mqtt
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        # client.username_pw_set("SPMlWZKRd0k9hc1D33Zvi11ncQWUBPJiujrg60X9Q77V7WoZQciW3793NVNdAkjS","")
        client.connect(MQTT_SERVER, MQTT_PORT, 60)
        client.loop_forever()
    except Exception as ex:
        print("[MQTT]failed to connect or receive msg from mqtt, due to: \n {0}".format(ex))
