import os
import urllib.request
import json
import datetime
import getDataLibv2
import requests
import time
import logger
from logger import LogType

url = "http://IP/rpc/"

# open log
logger.openLog()
logger.Print("Program started")

# function for exiting
def bye():
    logger.Print("Bye!")
    logger.closeLog()
    exit()
    
# function for loading properties for application
def loadProp():
    try:
        global url
        propF = open("properties.conf")
        data = json.loads(propF.read())
        url = url.replace("IP", data["relayIP"])
        propF.close()
        return 0
    except:
        return -1

# let's load properties and exit if something goes wrong
if loadProp() == -1:
    logger.Print("Properties file missing or invalid format. Ending process.")
    bye()

# returns http get response. Needs shelly rpc command as argument. For example schedule.list returns http://[ip]/rpc/schedule.list http get response
def httpGet(args):
    rtn = str(urllib.request.urlopen(url + args).read())
    return rtn

# returns 0 or -1 based on http post call success. Takes post json object as arugemnt.
def httpPost(myobj):
    c = requests.post(url, json = myobj)
    if "200" in str(c):
        return 0
    return -1

# checks if Shelly relay has same schedule as argument hours. return true or false
def checkInformation(activehours):
    h = httpGet("Schedule.List")

    # formats response format to correct json
    raw = json.loads(h[2:len(h) - 13] + "}")

    if int(str(raw['jobs'][0]['timespec']).split(' ')[2]) != activehours[0]:
        return False
    if int(str(raw['jobs'][1]['timespec']).split(' ')[2]) != activehours[1]:
        return False
    return True

def getPowerHours():
    try:
        prop = open("properties.conf", "r")
        dat = json.loads(str(prop.read()))
        startTime = int(dat["starttime"])
        startDay = int(dat["startday"])
        endTime = int(dat["endtime"])
        endDay = int(dat["endday"])
        onDuration = int(dat["onhours"])
        prop.close()
    except:
        return -1

    prcs = getDataLibv2.loadPrices()
    if type(prcs) != type([]) and prcs < 0:
        return -2
    ts = getDataLibv2.applyTimeSection(prcs, startDay, startTime, endDay, endTime)
    if type(ts) != type([]) and ts < 0:
        return -3
    chps = getDataLibv2.getCheapestInRow(ts, onDuration)
    if type(chps) != type([]) and chps < 0:
        return -3
    rtn = getDataLibv2.combineTimes(chps)
    if type(rtn) != type([]) and rtn < 0:
        return -3
    return rtn[0]

# main function of script.
def update():
    success = 0
    values = 0
    newUpdateTime = 0
    avg = 0

    # loads last update time
    f = open("data.temp", 'r')
    lstUpd = json.loads(f.read())
    f.close()
    lastUpdated = datetime.datetime.strptime(lstUpd['date'], '%Y-%m-%d %H:%M:%S')

    # download new data
    to = 0
    while 1:
        # exits if theres too many tries
        if to > 10:
            logger.Print("Update failed and aborted", LogType.ERROR)
            return

        # loads new hours, average price and updatetime based on price api data
        # values, avg, newUpdateTime = getDataLib.GetLowestWholeHours(lastUpdated)
        values = getPowerHours()
        logger.Print(f"Next cycle: {values}")
        
        # error handling if reurned error code
        if type(values) != type([]):
            if values < 0:
                if values == -1:
                    logger.Print("Properties file missing or invalid format",LogType.ERROR)
                    bye()
                if values == -2:
                    logger.Print("Http error", LogType.WARNING)
                elif values == -3:
                    logger.Print("Parse error", LogType.WARNING)
        else:
            # checks if relay is already up to date. if not, break the loop and continue script
            if checkInformation(values) == True and str(datetime.datetime.now().strftime("%Y-%m-%d")) == str(lastUpdated.date()):
                logger.Print("Alredy updated")
                return
            break

        # if failed, wait before retry
        to += 1
        time.sleep(10)

    # uploads new schedule to Shelly
    tries = 0
    while 1:
        logger.Print("Uploading..")
        # exits if theres too many tries
        if tries > 5:
            logger.Print("Data upload failed", LogType.ERROR)
            return
        tries += 1

        # upload new schedule for relay activation and deactivation
        chk = httpPost({"id":1,"method":"Schedule.Update","params":{"id":1,"timespec":str(f"0 0 {values[0]} * * SUN,MON,TUE,WED,THU,FRI,SAT")}})
        chk -= httpPost({"id":2,"method":"Schedule.Update","params":{"id":2,"timespec":str(f"0 0 {values[1]} * * SUN,MON,TUE,WED,THU,FRI,SAT")}})
        
        # if success, chk sould be 0
        if chk == 0:
            # double check that correct is uploaded
            if checkInformation(values) == True:
                logger.Print("Information match")
            else:
                logger.Print("Information dont match", LogType.WARNING)
                time.sleep(10)
                continue
            logger.Print("Data uploaded successfully")
            success = 1
            break

        time.sleep(10)

    # if upload was succeed, save update date to data.temp
    if success == 1:
        jsonFormat = json.dumps({'date':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'values':str(values), 'avg':round(avg, 2)})
        logger.Print(jsonFormat)
        f1 = open("data.temp", 'a')
        f1.truncate(0)
        f1.write(jsonFormat)
        f1.close()

update()
bye()