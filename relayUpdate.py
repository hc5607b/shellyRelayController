import os
import urllib.request
import json
import datetime
import getDataLib
import requests
import time

workingDir = ''

def loadProp():
    try:
        propF = open("properties.conf")
        workingDir = json.loads(propF.read())["scriptlocation"]
        propF.close()
        return 0
    except:
        return -1

if loadProp() == -1:
    print("Properties file missing or invalid format")
    exit()

logfile = open(workingDir + 'log.txt', 'a')
def log(dat):
    print(dat)
    logfile.write(f"[{datetime.datetime.now()}] {str(dat)}\n")

url = "http://192.168.10.150/rpc/"
def httpGet(args):
    rtn = str(urllib.request.urlopen(url + args).read())
    return rtn

def httpPost(myobj):
    c = requests.post(url, json = myobj)
    if "200" in str(c):
        return 0
    return -1

def checkInformation(activehours):
    h = httpGet("schedule.list")
    raw = json.loads(h[2:len(h) - 5])
    
    if int(str(raw['jobs'][0]['timespec'])[4]) != activehours[0]:
        return False
    if int(str(raw['jobs'][1]['timespec'])[4]) - 1 != activehours[len(activehours) - 1]:
        return False
    return True


def update():
    success = 0
    values = 0
    newUpdateTime = 0
    avg = 0

    f = open(workingDir+"data.temp", 'r')
    con = json.loads(f.read())
    f.close()
    lastUpdated = datetime.datetime.strptime(con['date'], '%Y-%m-%d %H:%M:%S')
    log(f"Last updated: {lastUpdated}")

    to = 0
    while 1:
        if to > 10:
            log("Update failed and aborted")
            return
        values, avg, newUpdateTime = getDataLib.GetLowestWholeHours(lastUpdated)
        
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
            
            if checkInformation(values) == True and newUpdateTime.date() == lastUpdated.date():
                log("Alredy updated")
                return
            break
        to += 1
        time.sleep(10)

    # log(values)
    tries = 0
    while 1:
        log("Uploading..")
        if tries > 5:
            log("Data upload failed")
            return
        tries += 1
        chk = httpPost({"id":1,"method":"Schedule.Update","params":{"id":1,"timespec":str(f"0 0 {values[0]} * * SUN,MON,TUE,WED,THU,FRI,SAT")}})
        chk += httpPost({"id":2,"method":"Schedule.Update","params":{"id":2,"timespec":str(f"0 0 {values[len(values)-1] + 1} * * SUN,MON,TUE,WED,THU,FRI,SAT")}})
        if chk == 0:

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

    if success == 1:
        jsonFormat = json.dumps({'date':str(newUpdateTime),'values':str(values), 'avg':round(avg, 2)})
        log(jsonFormat)
        f1 = open(workingDir+"data.temp", 'a')
        f1.truncate(0)
        f1.write(jsonFormat)
        f1.close()

update()
logfile.close()