#!/usr/bin/env python3

# web application GUI


from flask import Flask, render_template, request, jsonify, url_for, json
import csv
import shutil
from datetime import datetime
from flask_googlecharts import GoogleCharts
from flask_googlecharts import BarChart, MaterialLineChart, ColumnChart
from flask_googlecharts.utils import prep_data
from config import COLLECT_CAMERAS_MVSENSE_CAPABLE
from compute import *
import time
#import datetime

app = Flask(__name__)
charts = GoogleCharts(app)


@app.route('/', methods=['GET','POST'])
def index():
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
    return render_template("index.html",data=data)

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

@app.route('/mvOverview',methods=['GET','POST'])
def mvOverview():
    # extract MVSense over view data for a camera from the analytics API
    MVZones = []
    animation_option = {"startup": True, "duration": 1000, "easing": 'out'}

    #TODO: change theSERIAL for the actual serial number of the camera for which we are retrieving data which
    #should be provided bye the form when user clicks on a specific Zone bar within a specific Cameras chart

    theSERIAL='Q2EV-2QFS-YRYE'

    if request.method == 'POST':
        # This is for the historical detail
        data = getMVHistory(theSERIAL,'0')
        if data != 'link error':


            print("getMVHistory returned:", data)

            MVHistory = json.loads(data)
            # add a chart

            # now create the chart object using the serial as the name and the name of the device as the title
            mv_history_chart = ColumnChart("mvhistorychart", options={"title": "History Details",
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

            for j in range(len(MVHistory)):
                # grab all events in MVHistory, then
                # tabulate and summarize in hour blocks
                # example startTS: "2019-08-05T17:06:46.312Z" example endTs: "2019-08-05T17:07:46.312Z"
                # also, for each hour that has entrances, select the timeframe where there are
                # the most and extract a snapshot 30 seconds after that timestamp to show below in the page

                thisStartTs = MVHistory[j]["startTs"]
                thisEndTs = MVHistory[j]["endTs"]
                thisHour = thisEndTs.partition('T')[2][:2]
                thisMinuteMedTimestamp= time.mktime(datetime.strptime(thisEndTs, "%Y-%m-%dT%H:%M:%S.%fZ").timetuple())-30
                thisMinuteMedISOts=datetime.fromtimestamp(thisMinuteMedTimestamp).isoformat()+"Z"
                #print("Timestamp string:",thisEndTs )
                #print("Numerical equivalent: ", thisMinuteMedTimestamp)
                #print("ISO equivalent: ", thisMinuteMedISOts)

                thisEntrances = MVHistory[j]["entrances"]

                if thisHour in theHoursDict.keys():
                    #increase the number of entrances of this hour slot
                    theHoursDict[thisHour]=theHoursDict[thisHour]+thisEntrances
                    #check to see if the entrances for this minute are the most for this hour
                    if thisEntrances>theHoursMaxEntrancesDict[thisHour]:
                        #if so, make these entrances the most for the timeframe and save the timestamp for the
                        #middle of the minute with the most entrances
                        theHoursMaxEntrancesDict[thisHour]=thisEntrances
                        theHoursMaxEntrancesTimestampDict[thisHour]=thisMinuteMedISOts
                else:
                    #if this is the first time we see this timeslot, make the current entrances
                    #the starting balance for the dict entry
                    theHoursDict[thisHour] = thisEntrances
                    theHoursMaxEntrancesDict[thisHour] = thisEntrances
                    #only keep timestamp if there is at least one entry detected
                    if thisEntrances>0:
                        theHoursMaxEntrancesTimestampDict[thisHour] = thisMinuteMedISOts
                    else:
                        theHoursMaxEntrancesTimestampDict[thisHour]=''

            for dEntryKey in theHoursDict.keys():
                the_rows.append([dEntryKey, theHoursDict[dEntryKey]])

            mv_history_chart.add_rows(the_rows)
            charts.register(mv_history_chart)

            print("Max Entrances Timestamps: ", theHoursMaxEntrancesTimestampDict)

            #theScreenshots is an array of arays in the format [ timestamp string,  snapshot URL ]
            #this is to be passed to the form that will render them
            theScreenshots=[]

            for dTimeStampKey in theHoursMaxEntrancesTimestampDict.keys():
                if theHoursMaxEntrancesTimestampDict[dTimeStampKey]!='':
                    screenShotURLdata=getCameraScreenshot(theSERIAL,theHoursMaxEntrancesTimestampDict[dTimeStampKey])
                    print("getCameraSCreenshot returned: ",screenShotURLdata)
                    if  screenShotURLdata != 'link error':
                        screenShotURL = json.loads(screenShotURLdata)
                        theScreenshots.append([ theHoursMaxEntrancesTimestampDict[dTimeStampKey], screenShotURL["url"]])

            # wait for the URLs to be valid
            print("Waiting 10 seconds...")
            time.sleep(10)
            return render_template("mvHistory.html", historyChart=mv_history_chart, snapshotsArray=theScreenshots)
    else:
        # this is for the GET to show the overview
        devices_data=getDevices()
        if devices_data != 'link error':

            AllDevices=json.loads(devices_data)

            theDeviceCharts=[]
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
                # add a chart
                #first add the name of the chart to the list of charts to be displayed in the page
                theDeviceCharts.append("chart"+str(theChartNum))

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
                    the_rows.append([ "Zone "+str(thisZone["zoneId"]), thisZone["entrances"] ])
                    # store away the zoneID and serial of the camera to pass to the form so when someone clicks
                    # on a bar or button to expand detail, it comes back to this function in the POST section
                    # to know which zone from which camera to use
                    # also, put the zone name above, not the zone number since it is too big
                    # and messes up the graph
                mv_overview_chart.add_rows(the_rows)
                charts.register(mv_overview_chart)

                theChartNum+=1

            return render_template("mvOverview.html",allTheCharts=theDeviceCharts)

        else:
            return render_template('error.html'), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
