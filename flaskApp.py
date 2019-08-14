#!/usr/bin/env python3

# web application GUI


from flask import Flask, render_template, request, jsonify, url_for, json
import csv
import shutil
from datetime import datetime
from flask_googlecharts import GoogleCharts
from flask_googlecharts import BarChart, MaterialLineChart, ColumnChart
from flask_googlecharts.utils import prep_data
from config import COLLECT_CAMERAS_MVSENSE_CAPABLE, NETWORK_ID
from compute import *
import time
import pytz    # $ pip install pytz
import tzlocal # $ pip install tzlocal

app = Flask(__name__)
charts = GoogleCharts(app)


@app.route('/rawCMX', methods=['GET','POST'])
def rawCMX():
    if request.method == 'POST':
        select = flask.request.form.get('select')
        if select == 'cmxTimes':
            return cmxTimes()
    # open cmx data
    data = []
    with open('cmxData.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        arrayCount=0
        flag=0
        for row in reader:
            if row['MAC'] != '' and flag==0:
                count = 0
                flag = 1
                data.append({'MAC':row['MAC'],'timestamps':[{'ts':datetime.fromtimestamp(float(row['time'])).strftime('%m-%d,%H:%M'),'rssi':row['rssi']}]})
            elif row['MAC'] != '' and flag==1:
                arrayCount = arrayCount+1
                count = 0
                data.append({'MAC':row['MAC'],'timestamps':[{'ts':datetime.fromtimestamp(float(row['time'])).strftime('%m-%d,%H:%M'),'rssi':row['rssi']}]})
            elif row['MAC'] == '':
                count = count+1
                data[arrayCount]['timestamps'].append({'ts':datetime.fromtimestamp(float(row['time'])).strftime('%m-%d,%H:%M'),'rssi':row['rssi']})
    return render_template("rawCMX.html",data=data)

@app.route('/cmxTimes', methods=['GET','POST'])
def cmxTimes():

#testing graphs with chart.js

    # open cmx data
    data = []
    with open('cmxData.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        arrayCount=0
        flag=0
        for row in reader:
            if row['MAC'] != '' and flag==0:
                count = 0
                flag = 1
                data.append({'MAC':row['MAC'],'timestamps':{count:row['time']}})
            elif row['MAC'] != '' and flag==1:
                arrayCount = arrayCount+1
                count = 0
                data.append({'MAC':row['MAC'],'timestamps':{count:row['time']}})
            elif row['MAC'] == '':
                count = count+1
                data[arrayCount]['timestamps'][count]=row['time']
    # print(len(data[0]['timestamps']))
    cmxData=getCMXHours(data)
    for x in cmxData:
        for y in range(len(x['timeData'])):
            x['timeData'][y]['firstSeen'] = datetime.fromtimestamp(float(x['timeData'][y]['firstSeen'])).strftime('%m-%d,%H:%M')
            x['timeData'][y]['lastSeen'] = datetime.fromtimestamp(float(x['timeData'][y]['lastSeen'])).strftime('%m-%d,%H:%M')


    labels = ["January", "February", "March", "April", "May", "June", "July", "August"]
    values = [10, 9, 8, 7, 6, 4, 7, 8]

    return render_template("cmxTimes.html",cmxData=cmxData, cmxvalues=values, cmxlabels=labels)

@app.route("/testchartdata")
def testchartdata():

    d = {"cols": [{"id": "", "label": "Date", "pattern": "", "type": "date"},
                  {"id": "", "label": "Spectators", "pattern": "", "type": "number"}],
         "rows": [{"c": [{"v": datetime(2016, 5, 1), "f": None}, {"v": 3987, "f": None}]},
                  {"c": [{"v": datetime(2016, 5, 2), "f": None}, {"v": 6137, "f": None}]},
                  {"c": [{"v": datetime(2016, 5, 3), "f": None}, {"v": 9216, "f": None}]},
                  {"c": [{"v": datetime(2016, 5, 4), "f": None}, {"v": 22401, "f": None}]},
                  {"c": [{"v": datetime(2016, 5, 5), "f": None}, {"v": 24587, "f": None}]}]}

    return jsonify(prep_data(d))

@app.route('/hourFilter', methods=['GET','POST'])
def hourFilter():
    # testing graphs with Google Charts
    animation_option={ "startup" : True, "duration": 1000, "easing":'out'}

    hot_dog_chart = BarChart("hot_dogs", options={"title": "Contest Results",
                                                  "width": 500,
                                                  "height": 300,
                                                  "animation": animation_option})
    hot_dog_chart.add_column("string", "Competitor")
    hot_dog_chart.add_column("number", "Hot Dogs")
    hot_dog_chart.add_rows([["Matthew Stonie", 62],
                            ["Joey Chestnut", 60],
                            ["Eater X", 35.5],
                            ["Erik Denmark", 33],
                            ["Adrian Morgan", 31]])
    charts.register(hot_dog_chart)

    # total store traffic with material line charts
    animation_option={ "startup" : True, "duration": 1000}
    spectators_chart = MaterialLineChart("spectators",
                                         options={"title": "Contest Spectators",
                                                  "width": 500,
                                                  "height": 300
                                                  },
                                         data_url=url_for('testchartdata'))

    charts.register(spectators_chart)



    # open cmx data
    data = []
    with open('cmxData.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        arrayCount=0
        flag=0
        for row in reader:
            if row['MAC'] != '' and flag==0:
                count = 0
                flag = 1
                data.append({'MAC':row['MAC'],'timestamps':{count:row['time']}})
            elif row['MAC'] != '' and flag==1:
                arrayCount = arrayCount+1
                count = 0
                data.append({'MAC':row['MAC'],'timestamps':{count:row['time']}})
            elif row['MAC'] == '':
                count = count+1
                data[arrayCount]['timestamps'][count]=row['time']
    # print(len(data[0]['timestamps']))
    cmxData=cmxFilterHours(data)
    for x in cmxData:
        for y in range(len(x['timeData'])):
            x['timeData'][y]['firstSeen'] = datetime.fromtimestamp(float(x['timeData'][y]['firstSeen'])).strftime('%m-%d,%H:%M')
            x['timeData'][y]['lastSeen'] = datetime.fromtimestamp(float(x['timeData'][y]['lastSeen'])).strftime('%m-%d,%H:%M')
    print(cmxData)
    return render_template("filterTimes.html",cmxData=cmxData)



@app.route('/mvSense',methods=['GET','POST'])
def mvSense():
    # open mv sense data
    data = []
    with open('mvData.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        arrayCount=0
        flag=0
        for row in reader:
            print(row['Time In'])
            link = getMVLink('Q2EV-2QFS-YRYE',row['Time In'])
            link = link.replace('{"url":"',"")
            link = link.replace('"}',"")
            data.append({'timeIn':datetime.fromtimestamp(float(row['Time In'])/1000).strftime('%m-%d,%H:%M'),'timeOut':datetime.fromtimestamp(float(row['Time Out'])/1000).strftime('%m-%d,%H:%M'),'count':row['Count'],'link':link})
    # print(len(data[0]['timestamps']))
    return render_template("mvSense.html",data=data)

@app.route('/cmxActivity',methods=['GET','POST'])
def cmxActivity():
    # open cmx data
    data = []
    with open('cmxData.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        arrayCount=0
        flag=0
        for row in reader:
            if row['MAC'] != '' and flag==0:
                count = 0
                flag = 1
                data.append({'MAC':row['MAC'],'timestamps':{count:row['time']}})
            elif row['MAC'] != '' and flag==1:
                arrayCount = arrayCount+1
                count = 0
                data.append({'MAC':row['MAC'],'timestamps':{count:row['time']}})
            elif row['MAC'] == '':
                count = count+1
                data[arrayCount]['timestamps'][count]=row['time']
    newData = computeCMXActivity(data)

    #add a chart
    animation_option={ "startup" : True, "duration": 1000, "easing":'out'}

    cmx_activity_chart = ColumnChart("cmx_activity", options={"title": "CMX Activity",
                                                  "width": 1000,
                                                  "height": 500,
                                                  "hAxis.title": "Hour",
                                                  "animation": animation_option})
    cmx_activity_chart.add_column("string", "Hour of the day")
    cmx_activity_chart.add_column("number", "Devices")
    print(newData)
    the_rows = []
    for i in range(24):
        the_rows.append([str(i+1),newData[i]])
    cmx_activity_chart.add_rows(the_rows)

    charts.register(cmx_activity_chart)
    return render_template("cmxActivity.html",x=newData)


@app.route('/mvActivity',methods=['GET','POST'])
def mvActivity():
    # open mv sense data
    data = []
    with open('mvData.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        arrayCount=0
        flag=0
        for row in reader:
            data.append({'timeIn':row['Time In'],'timeOut':row['Time Out'],'count':row['Count']})
    newData = computeMVActivity(data)
    # print(len(data[0]['timestamps']))
    return render_template("mvActivity.html",x=newData)

@app.route('/correlation',methods=['GET','POST'])
def correlation():
    # open cmx data
    data = []
    print("Reading CMX Data...")
    with open('cmxData.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        arrayCount=0
        flag=0
        for row in reader:
            if row['MAC'] != '' and flag==0:
                count = 0
                flag = 1
                data.append({'MAC':row['MAC'],'timestamps':[{'ts':row['time'],'rssi':row['rssi']}]})
            elif row['MAC'] != '' and flag==1:
                arrayCount = arrayCount+1
                count = 0
                data.append({'MAC':row['MAC'],'timestamps':[{'ts':row['time'],'rssi':row['rssi']}]})
            elif row['MAC'] == '':
                count = count+1
                data[arrayCount]['timestamps'].append({'ts':row['time'],'rssi':row['rssi']})
    # open mv sense data
    print("Reading MVSense Data...")
    mvData = []
    with open('mvData.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        arrayCount=0
        flag=0
        for row in reader:
            mvData.append({'timeIn':row['Time In'],'timeOut':row['Time Out'],'count':row['Count']})
    print("Computing co-relation...")
    newData = getCorrelation(data,mvData)
    return render_template("correlation.html",correlation=newData)

@app.route('/',methods=['GET'])
def index():
    # this is for the GET to show the overview
    return render_template("pleasewait.html", theReason='Getting all cameras for network: ' + NETWORK_ID)


@app.route('/mvOverview',methods=['GET','POST'])
def mvOverview():
    # extract MVSense over view data for a camera from the analytics API
    MVZones = []
    animation_option = {"startup": True, "duration": 1000, "easing": 'out'}

    #First we have the logic for creating the page with all the historical details of zone below,
    #further down is the logic to show the Overview of all cameras and their respective zones
    if request.method == 'POST':
        # This is for the historical detail
        zoneDetails = request.form['zone_details']
        print("zoneDetails=",zoneDetails)
        #zoneDetailsTuple contains: [camera serial, camera name, zone id, zone name]
        zoneDetailsTuple=zoneDetails.split(',')
        theSERIAL=zoneDetailsTuple[0]
        theCameraNAME=zoneDetailsTuple[1]
        theZoneID=zoneDetailsTuple[2]
        theZoneNAME=zoneDetailsTuple[3]

        data = getMVHistory(theSERIAL,theZoneID)
        if data != 'link error':


            print("getMVHistory returned:", data)

            MVHistory = json.loads(data)
            # add a chart

            # now create the chart object using the serial as the name and the name of the device as the title
            mv_history_chart = ColumnChart("mvhistorychart", options={"title": "Camera: "+theCameraNAME+" Zone: "+theZoneNAME,
                                                                                 "width": 1000,
                                                                                 "height": 500,
                                                                                 "hAxis.title": "Hour",
                                                                                 "animation": animation_option})
            mv_history_chart.add_column("string", "Zone")
            mv_history_chart.add_column("number", "Visitors")
            print(data)
            the_rows = []
            theHoursDict = dict()
            theHoursMaxEntrancesDict = dict()
            theHoursMaxEntrancesTimestampDict = dict()
            theLocalHoursMaxEntrancesTimestampDict = dict()

            for j in range(len(MVHistory)):
                # grab all events in MVHistory, then
                # tabulate and summarize in hour blocks
                # example startTS: "2019-08-05T17:06:46.312Z" example endTs: "2019-08-05T17:07:46.312Z"
                # also, for each hour that has entrances, select the timeframe where there are
                # the most and extract a snapshot 30 seconds after that timestamp to show below in the page

                thisStartTs = MVHistory[j]["startTs"]
                thisEndTs = MVHistory[j]["endTs"]

                thisHour = thisEndTs.partition('T')[2][:2]

                theEndTsTimeStamp=datetime.strptime(thisEndTs, "%Y-%m-%dT%H:%M:%S.%fZ")

                thisMinuteMedTimestamp= time.mktime(theEndTsTimeStamp.timetuple())-30
                thisMinuteMedISOts=datetime.fromtimestamp(thisMinuteMedTimestamp).isoformat()+"Z"

                #convert to localtimezone
                local_timezone = tzlocal.get_localzone()  # get pytz tzinfo
                local_timezone_str = str(local_timezone)
                theLocalEndTsTimeStamp = theEndTsTimeStamp.replace(tzinfo=pytz.utc).astimezone(local_timezone)

                thislocalMinuteMedTimestamp= time.mktime(theLocalEndTsTimeStamp.timetuple())-30
                thislocalMinuteMedISOts = datetime.fromtimestamp(thislocalMinuteMedTimestamp).isoformat() + "Z"
                localHour = thislocalMinuteMedISOts.partition('T')[2][:2]

                #print("Timestamp string:",thisEndTs )

                #print("Numerical equivalent: ", thisMinuteMedTimestamp)
                #print("Local Numerical equivalent: ", thislocalMinuteMedTimestamp)
                #print("ISO equivalent: ", thisMinuteMedISOts)
                #print("local ISO equivalent: ", thislocalMinuteMedISOts)

                thisEntrances = MVHistory[j]["entrances"]

                # Now we will use localHour instead of thisHour as the Dict key to hold the accounting for body
                # detection per hour since that is what is shown on the graph, it should behave the same otherwise
                # as when we used thisHour originally, but show a local hour instead of UTC which was confusing.

                if localHour in theHoursDict.keys():
                    #increase the number of entrances of this hour slot
                    theHoursDict[localHour]=theHoursDict[localHour]+thisEntrances
                    #check to see if the entrances for this minute are the most for this hour
                    if thisEntrances>theHoursMaxEntrancesDict[localHour]:
                        #if so, make these entrances the most for the timeframe and save the timestamp for the
                        #middle of the minute with the most entrances
                        theHoursMaxEntrancesDict[localHour]=thisEntrances
                        theHoursMaxEntrancesTimestampDict[localHour]=thisMinuteMedISOts
                        #keep track of local version as well
                        theLocalHoursMaxEntrancesTimestampDict[localHour]=thislocalMinuteMedISOts

                else:
                    #if this is the first time we see this timeslot, make the current entrances
                    #the starting balance for the dict entry
                    theHoursDict[localHour] = thisEntrances
                    theHoursMaxEntrancesDict[localHour] = thisEntrances
                    #only keep timestamp if there is at least one entry detected
                    if thisEntrances>0:
                        theHoursMaxEntrancesTimestampDict[localHour] = thisMinuteMedISOts
                        theLocalHoursMaxEntrancesTimestampDict[localHour] = thislocalMinuteMedISOts
                    else:
                        theHoursMaxEntrancesTimestampDict[localHour]=''
                        theLocalHoursMaxEntrancesTimestampDict[localHour]=''


            for dEntryKey in theHoursDict.keys():
                the_rows.append([dEntryKey, theHoursDict[dEntryKey]])

            mv_history_chart.add_rows(the_rows)
            charts.register(mv_history_chart)

            print("Max Entrances Timestamps: ", theHoursMaxEntrancesTimestampDict)
            print("Max Local Entrances Timestamps: ", theLocalHoursMaxEntrancesTimestampDict)

            #theScreenshots is an array of arays in the format [ timestamp string,  snapshot URL ]
            #this is to be passed to the form that will render them
            theScreenshots=[]

            for dTimeStampKey in theHoursMaxEntrancesTimestampDict.keys():
                if theHoursMaxEntrancesTimestampDict[dTimeStampKey]!='':
                    screenShotURLdata=getCameraScreenshot(theSERIAL,theHoursMaxEntrancesTimestampDict[dTimeStampKey])
                    print("getCameraSCreenshot returned: ",screenShotURLdata)
                    if  screenShotURLdata != 'link error':
                        screenShotURL = json.loads(screenShotURLdata)
                        #Passing theLocalHoursMaxEntrancesTimestampDict[dTimeStampKey] instead of theHoursMaxEntrancesTimestampDict[dTimeStampKey] below
                        #to show a local timestamp we calculated in a previous loop
                        theScreenshots.append([ theLocalHoursMaxEntrancesTimestampDict[dTimeStampKey], screenShotURL["url"]])

            # wait for the URLs to be valid
            print("Waiting 10 seconds...")
            time.sleep(10)
            return render_template("mvHistory.html", historyChart=mv_history_chart, snapshotsArray=theScreenshots, localTimezone=local_timezone_str)
    else:

        devices_data=getDevices()
        if devices_data != 'link error':

            AllDevices=json.loads(devices_data)

            #theDeviceCharts is just a list (array) of the names of the charts constructed with the
            #google charts flask library. They are to be iterated through to place on the History/details page
            theDeviceCharts=[]
            #theDeviceDetails is a list of the details of each camera device. Each entry has a serial number, label and
            #a list of zones for which there is zoneID and label
            theDeviceDetails=[]

            theChartNum=0

            for theDevice in AllDevices:
                theModel=theDevice["model"]

                if theModel[:4] not in COLLECT_CAMERAS_MVSENSE_CAPABLE:
                    continue

                data=getMVOverview(theDevice["serial"])
                if data == 'link error':
                    continue

                print("getMVOverview returned:" , data)
                MVZones=json.loads(data)

                zonesdetaildata=getMVZones(theDevice["serial"])
                if zonesdetaildata == 'link error':
                    continue

                print("getMVZones returned:" , zonesdetaildata)
                MVZonesDetails=json.loads(zonesdetaildata)

                # add a chart
                #first add the name of the chart to the list of charts to be displayed in the page
                theDeviceCharts.append("chart"+str(theChartNum))

                #now append the top level details of the camera for this chart to theDeviceDetails
                theDeviceDetails.append([theDevice["serial"],theDevice["name"],[]])

                #now create the chart object using the serial as the name and the name of the device as the title
                mv_overview_chart = ColumnChart("chart"+str(theChartNum), options={"title": theDevice["name"],
                                                                          "width": 800,
                                                                          "height": 400,
                                                                          "hAxis.title": "Hour",
                                                                          "animation": animation_option})
                mv_overview_chart.add_column("string", "Zone")
                mv_overview_chart.add_column("number", "Visitors")
                print(data)
                the_rows = []
                for j in range(len(MVZones)):
                    thisZone=MVZones[j]
                    #assuming same number of zone entries overviews than number of zones here
                    thisZoneDetails=MVZonesDetails[j]
                    the_rows.append([ str(thisZoneDetails["label"]), thisZone["entrances"] ])
                    # store away the zoneID and serial of the camera to pass to the form so when someone clicks
                    # on a bar or button to expand detail, it comes back to this function in the POST section
                    # to know which zone from which camera to use


                    #we are assuming below that we have a chart per each MV capable camera, if that changes
                    # we need to figure out aonther way to index theDeviceDetails or use some other method
                    # to store/retrieve the data besides a list of lists
                    theDeviceDetails[theChartNum][2].append([thisZoneDetails["zoneId"], thisZoneDetails["label"]])

                mv_overview_chart.add_rows(the_rows)
                charts.register(mv_overview_chart)

                theChartNum+=1

            print("Rendering overview form with:")
            print("allTheDetails=",theDeviceDetails)

            return render_template("mvOverview.html",allTheCharts=theDeviceCharts,allTheDetails=theDeviceDetails)

        else:
            return render_template('error.html'), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
