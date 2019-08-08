# code pulls cmx data from Meraki access point and saves in cmxData.csv file
# Libraries
from pprint import pprint
from flask import Flask
from flask import json
from flask import request
import sys, getopt
from datetime import datetime
from config import _RSSI_THRESHOLD, _APMACADDR, validator
import csv
import shutil
############## USER DEFINED SETTINGS ###############
# MERAKI SETTINGS
secret = ""
version = "2.0" # This code was written to support the CMX JSON version specified

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

# writes data to a .csv file
def updateData(data):
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
    main(sys.argv[1:])
    app.run(port=5000,debug=False)
