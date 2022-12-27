import os
import urllib.request
import json
import datetime
import getDataLib
import requests
import time

url = "http://IP/rpc/"

# function for loading properties for application
def loadProp():
    try:
        global url
        propF = open("properties.conf")
        url = url.replace("IP", json.loads(propF.read())["relayIP"])
        propF.close()
        return 0
    except:
        return -1

# let's load properties and exit if something goes wrong
if loadProp() == -1:
    print("Properties file missing or invalid format. Ending process.")
    exit()

# open log file
logfile = open('log.txt', 'a')
def log(dat):
    print(dat)
    logfile.write(f"[{datetime.datetime.now()}] {str(dat)}\n")

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
    h = httpGet("schedule.list")

    # formats response format to correct json
    raw = json.loads(h[2:len(h) - 5])
    
    if int(str(raw['jobs'][0]['timespec'])[4]) != activehours[0]:
        return False
    if int(str(raw['jobs'][1]['timespec'])[4]) - 1 != activehours[len(activehours) - 1]:
        return False
    return True

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
            log("Update failed and aborted")
            return

        # loads new hours, average price and updatetime based on price api data
        values, avg, newUpdateTime = getDataLib.GetLowestWholeHours(lastUpdated)
        
        # error handling if reurned error code
        if type(values) != type([]):
            if values < 0:
                if values == -2:
                    log("Http error")
                elif values == -3:
                    log("Parse error")
                elif values == -4:
                    log("Data not found")
                elif values == -5:
                    log("Properties file missing or invalid format")
                    return
        else:
            # checks if relay is already up to date. if not, break the loop and continue script
            if checkInformation(values) == True and newUpdateTime.date() == lastUpdated.date():
                log("Alredy updated")
                return
            break

        # if failed, wait before retry
        to += 1
        time.sleep(10)

    # uploads new schedule to Shelly
    tries = 0
    while 1:
        log("Uploading..")
        # exits if theres too many tries
        if tries > 5:
            log("Data upload failed")
            return
        tries += 1

        # upload new schedule for relay activation and deactivation
        chk = httpPost({"id":1,"method":"Schedule.Update","params":{"id":1,"timespec":str(f"0 0 {values[0]} * * SUN,MON,TUE,WED,THU,FRI,SAT")}})
        chk -= httpPost({"id":2,"method":"Schedule.Update","params":{"id":2,"timespec":str(f"0 0 {values[len(values)-1] + 1} * * SUN,MON,TUE,WED,THU,FRI,SAT")}})

        # if success, chk sould be 0
        if chk == 0:
            # double check that correct is uploaded
            if checkInformation(values) == True:
                log("Information match")
            else:
                log("Information dont match")
                time.sleep(10)
                continue
            log("Data uploaded successfully")
            success = 1
            break

        time.sleep(10)

    # if upload was succeed, save update date to data.temp
    if success == 1:
        jsonFormat = json.dumps({'date':str(newUpdateTime),'values':str(values), 'avg':round(avg, 2)})
        log(jsonFormat)
        f1 = open("data.temp", 'a')
        f1.truncate(0)
        f1.write(jsonFormat)
        f1.close()

update()
logfile.close()