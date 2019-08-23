# Meraki MV and MX Analytics Demo

This demo utilizes Meraki MV Sense camera data in conjunction with Meraki CMX access point data to output human consumable information and correlations regarding activities such as number of visits, busiest times in a day, number of people etc.  Streaming data from MV sense and CMX are stored in local files and are then utilized for further analysis and formatting.  A web GUI is used to display and interact with the data with options for csv download.

It also implements a simplified dashboard that focuses on showing the number of visitors on each camera in a Network divided by zones and
zooming into a particular zone to see hourly details and relevant camera snapshots.
  
  
This application has relevant use cases for asset utilization tracking, customer activity tracking, and much more.

There are 3 main functionalities in this repository:  

   The **cmxreceiver.py** program receives streams of cmx data from Meraki access points and saves this data in cmxData.csv.  

   The **mvSense.py** program receives streams of MV Sense data from Meraki video cameras and stores this data in mvData.csv.   

   The **flaskApp.py** then utilizes functions in compute.py to analyze and format the data into a web application.  


## Configuration

**Config.py** contains all of the global variables and configuration needed throughout the code, including keys and thresholds.

### MV Sense Camera Setup  
Leverage Meraki new camera API and MQTT capability to create a notification service. When the camera detects a person consistently appears in a particular zone the service will send a Webex team message to a Webex team room with a video link which will directly go to the video footage when that even occurred. This is useful for alerting unexpected person movement in off-hours. Here is more information on MV sense data: https://developer.cisco.com/meraki/build/mv-sense-documentation/

—— MQTT and setting ——
1. In the Meraki dashboard, go to **Cameras > [Camera Name] > Settings > Sense** page.
2. Click **Add or edit MQTT Brokers > New MQTT Broker** and add you broker information. For testing/trial you can find public broker at [here](https://github.com/mqtt/mqtt.github.io/wiki/public_brokers).
3. You can install [MQTT.fx](https://mqttfx.jensd.de/) to subscribe to MQTT broker. This is a very useful tool

—— MV Sense Configuration ——
1. In the config.py file, there is a section for “variables utilized in mvSense.py” which contains all of the config variables for the MV Sense data gathering code
2. MQTT_SERVER is the MQTT broker ip or domain ("test.mosquitto.org" for example)
3. MQTT_PORT is the MQTT broker port being utilized (usually 1883)
4. MQTT_TOPIC is the top of the Meraki camera Matt, boy default it is “/merakimv/#”
5. MERAKI_API_KEY is the Meraki Api key for organization
6. NETWORK_ID is Camera's network ID, will use this get video link with camera api
7. COLLECT_CAMERAS_SERIAL_NUMBERS is the array of cameras serial numbers, for all of there cameras use *
8. COLLECT_ZONE_IDS is Array of camera zone id, all is *
9. MOTION_ALERT_PEOPLE_COUNT_THRESHOLD is the minimum number of people detected in camera to trigger the start of an activity
10. MOTION_ALERT_ITERATE_COUNT is the minimum number of mqtt messages counted to indicate that an activity has successfully occurred
11. MOTION_ALERT_TRIGGER_PEOPLE_COUNT is the minimum number of people needed to successfully complete and activity
12. MOTION_PAUSE_TIME is the pause time after alert finished triggering
13. TIMEOUT is the number of messages until action times out due to in activity (will then check whether minimum alert iterate count is met to determine activity success)



——------ CMX Access point Setup ------——
Cisco Meraki CMX Receiver is asimple example demonstrating how to interact with the CMX API.
How it works:
- Meraki access points will listen for WiFi clients that are searching for a network to join and log the events.
- The "observations" are then collected temporarily in the cloud where additional information can be added to
the event, such as GPS, X Y coordinates and additional client details.
- Meraki will first send a GET request to this CMX receiver, which expects to receive a "validator" key that matches
the Meraki network's validator.
- Meraki will then send a JSON message to this application's POST URL (i.e. http://yourserver/ method=[POST])
- The JSON is checked to ensure it matches the expected secret, version and observation device type.
- The resulting data is sent to the "save_data(data)" function where it can be sent to a database or other service
    - This example will simply print the CMX data to the console.
Default port: 5000
Cisco Meraki CMX Documentation
https://documentation.meraki.com/MR/Monitoring_and_Reporting/CMX_Analytics#CMX_Location_API

—— CMX Configuration ——
1. In the config.py file, there is a section for “Variables utilized in cmxreceiver.py” which contains all of the config variables for the cmx data gathering code
2. Validator is the validator key that can be found in the Meraki dashboard by navigating to **Network-wide > General
3. Scroll down to “Location and Analytics” to copy and paste this validator key into code (ensure analytics and scanning API are enabled)
4. _RSSI_THRESHOLD is the minimum rssi value needed for a device to be written into database (rssi is the signal strength of the device seen by the access point
5. _APMACADDR is the MAC address of the desired access point to gather data from

—— Access Point setting ——
1. Download ngrok which is used to create public URLs for programs (more information here: https://ngrok.com)
2. Use ngrok to expose port 5000 by entering ‘./ngrok http 5000’ into terminal
3. You should see a url created that looks similar to this ‘https://2a6eed03.ngrok.io/'
4. Copy and paste this url into the “Post URL” section of “Location and Analytics” in the Meraki Dashboard
5. Note that the validate button should fail at this point as the the cmx receiver is not up and running



——------ Computing Configuration ------——
1. In the config.py file, there is a section for “Variables utilized in compute.py"
2. _FILTER_TIME is the number of seconds in which devices will not be displayed if total time seen by cmx data is over this threshold
3. _SESSION_TIME is the number of seconds between cmx timestamps which is still considered to be the same session of activity (as sometimes gaps in streaming data can happens but this does not necessarily mean device has left and come back)
4. timeWindow defines a leeway period before inTime and after outTime of mvSense data in which cmx data should still be considered, as the times may not exactly match up due to granularity differences
5. rssiThreshold defines minimum signal strength to be considered in correlation with mvSense data and cmx data



——------ Running Code ------—— 
1. Make sure Python is installed
2. Make sure pip is installed (https://pip.pypa.io/en/stable/installing/ for more information on pip)
3. Enter 'pip install -r requirements.txt' into command line to download necessary libraries
4. Ensure all elements of the config.py file are completed
5. Ensure ngrok is running and that the url matches what is in the Meraki Dashboard (./ngrok http 5000)
6. In a new terminal window, enter ‘python3.7 cmxreceiver.py’ (note at this point the validate button in the Meraki dashboard should be working, data will stream every minute or so)
7. In a new terminal window, enter ‘python3.7 mvSense.py’ (connection should be made with MQTT server and data should start streaming)
8. To run the flask application, enter ‘python flaskApp.py’ in another terminal window and navigate your browser to the given url address (http://0.0.0.0:5001)
