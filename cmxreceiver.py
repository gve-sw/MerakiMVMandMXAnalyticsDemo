"""
Copyright (c) 2019 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

# code pulls cmx data from Meraki access point and saves in cmxData.csv file
# Libraries
from pprint import pprint
from flask import Flask
from flask import json
from flask import request
import sys, getopt
from datetime import datetime
from flaskApp import _APMACADDR, validator, db, cmxDataTbl
from config import _RSSI_THRESHOLD
import csv
import shutil
from flask_sqlalchemy import SQLAlchemy
############## USER DEFINED SETTINGS ###############
# MERAKI SETTINGS
secret = ""
version = "2.0" # This code was written to support the CMX JSON version specified

print("AP MAC Address: " + _APMACADDR)
print("Validator: " + validator)

# Parse CMX data
def matchMAC(cmx, mac):
    for x in cmx['data']['observations']:
        if x['clientMac'] == mac:
            # clientTime = x['seenEpoch']
            clientTime = datetime.utcfromtimestamp(x['seenEpoch']).strftime('%Y-%m-%d @ %H:%M:%S')
            print(x['clientMac'] + " found on " + clientTime)
            f = open('output.txt','a+')
            f.write(clientTime + "\n")
            f.close()
            sent_notification("client found @" + clientTime)
            return
    f = open('output.txt','a+')
    f.write('not found \n')
    f.close()
    sent_notification('client not found')
    return


def updateData(data):

    # use CSV to format data prior to pushing to database 
    with open('cmxData.csv','r') as csvfile, open('db.csv.temp','w',newline='') as temp:
        foundFlag = 0
        reader = csv.DictReader(csvfile)
        fieldnames = ['MAC', 'time','rssi']
        writer = csv.DictWriter(temp,fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            # writer.writerow(row)
            macAdd = row['MAC']
            if data['clientMac'] == macAdd and data['rssi'] >= _RSSI_THRESHOLD:
                foundFlag = 1
                writer.writerow({'MAC':data['clientMac'],'time':data['seenEpoch'],'rssi':data['rssi']})
                writer.writerow({'MAC':'','time':row['time'],'rssi':row['rssi']})
            else:
                writer.writerow(row)
        if foundFlag == 0 and data['rssi'] >= _RSSI_THRESHOLD:
            writer.writerow({'MAC':data['clientMac'],'time':data['seenEpoch'],'rssi':data['rssi']})
    shutil.move('db.csv.temp','cmxData.csv')

    
    #clear database table
    db.session.query(cmxDataTbl).delete()
    db.session.commit()
   
    #CSV to Database
    with open('cmxData.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        next(readCSV)
        for row in readCSV:
            cmxWrite = cmxDataTbl(mac=row[0], time=row[1], rssi=row[2])
            db.session.add(cmxWrite)
    db.session.commit()


# Save CMX Data for Recepcion
def save_data(data):
    # CHANGE ME - send 'data' to a database or storage system
    # pprint(data, indent=1)
    if data['data']['apMac']== _APMACADDR:
        print("---- SAVING CMX DATA ----")
        print(data)
        for x in data['data']['observations']:
            updateData(x)
        print("--- CMX DATA SAVED ---")




####################################################
app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

# Respond to Meraki with validator
@app.route('/', methods=['GET'])
def get_validator():
    print("validator sent to: ",request.environ['REMOTE_ADDR'])
    return validator

# Accept CMX JSON POST
@app.route('/', methods=['POST'])
def get_cmxJSON():
    if not request.json or not 'data' in request.json:
        return("invalid data",400)
    cmxdata = request.json
    #pprint(cmxdata, indent=1)
    print("Received POST from ",request.environ['REMOTE_ADDR'])

    # Verify secret
    if cmxdata['secret'] != secret:
        print("secret invalid:", cmxdata['secret'])
        return("invalid secret",403)
    else:
        print("secret verified: ", cmxdata['secret'])

    # Verify version
    if cmxdata['version'] != version:
        print("invalid version")
        return("invalid version",400)
    else:
        print("version verified: ", cmxdata['version'])

    # Determine device type
    if cmxdata['type'] == "DevicesSeen":
        print("WiFi Devices Seen")
        # matchMAC(cmxdata,MATCH_MAC_ADDRESS)
        print(cmxdata['data']['apMac'])
        save_data(cmxdata)
    elif cmxdata['type'] == "BluetoothDevicesSeen":
        print("Bluetooth Devices Seen")
    else:
        print("Unknown Device 'type'")
        return("invalid device type",403)

    # Do something with data (commit to database)
    # save_data(cmxdata)
    # matchMAC(cmxdata,MATCH_MAC_ADDRESS)

    # Return success message
    return "CMX POST Received"


# Launch application with supplied arguments
def main(argv):
    global validator
    global secret

    try:
       opts, args = getopt.getopt(argv,"hv:s:",["validator=","secret="])
    except getopt.GetoptError:
       print ('cmxreceiver.py -v <validator> -s <secret>')
       sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
           print ('cmxreceiver.py -v <validator> -s <secret>')
           sys.exit()
       elif opt in ("-v", "--validator"):
           validator = arg
       elif opt in ("-s", "--secret"):
           secret = arg
    print ('validator: '+validator)
    print ('secret: '+secret)


if __name__ == '__main__':
    from flaskApp import db
    main(sys.argv[1:])
    db.init_app(app)
    app.run(port=5000,debug=False)
