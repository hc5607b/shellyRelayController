import urllib.request
import json
import datetime

class Hour:
    def __init__(self, day, hour, price, timestamp):
        self.day = day
        self.hour = hour
        self.price = price
        self.timestamp = timestamp

    def __repr__(self):
        return f"Timestamp({self.day}, {self.hour}, {self.price})"

raw = ""
priceOfDay = -1
hours = []

startTime = 23
startDay = 0
endTime = 7
endDay = 1
onDuration = 3

def filterTime():
    global hours
    startID = -1
    endID = -1
    
    for i in range(0, len(hours)):
        if hours[i].day == startDay and hours[i].hour == startTime:
            startID = i
            continue
        if hours[i].day == endDay and hours[i].hour == endTime:
            endID = i
    
    if startID == -1 or endID == -1:
        return -1
    return hours[startID:endID]

def calcPowerHours():
    avgs = []
    for i in range(0, len(hours) - onDuration + 1):
        av = []
        for j in range(0, onDuration):
            av.append(hours[i+j].price)
        # print(av)
        avgs.append(sum(av) / onDuration)
    return avgs

def getLowestHours(sums):
    val = 9999999
    lID = -1
    for i in range(0,len(sums)):
        if sums[i] < val:
            val = sums[i]
            lID = i
    global priceOfDay 
    priceOfDay = val
    onHours = []
    _start = startTime + lID
    if _start > 23:
        _start = _start - 24
    for i in range(0, 3):
        nTime = _start + i
        if nTime > 23:
            nTime = nTime - 24
        onHours.append(nTime)
    return onHours

def GetLowestSingleHours():
    print(hours)
    print(len(hours))
    print(hours[0].price)
    slist = sorted(hours, key=lambda x: x.price)
    return slist[:onDuration]

def formatToJSON(arr):
    startT = arr[0]
    endT = arr[len(arr) - 1] + 1
    return '{"start":'+str(startT)+', "end":'+str(endT)+'}'

def init():
    global hours
    global raw
    hours = []

    hget = ""
    try:
        hget = urllib.request.urlopen("https://elspotcontrol.netlify.app/spotprices-v01-FI.json")
    except:
        return -1
    if hget.getcode() != 200:
        return -1

    raw = json.loads(hget.read())
    raw = raw['hourly_prices']

    for item in raw:
        hours.append(Hour(int(item.split('.')[0]), int(item.split('.')[1]), raw[item]['price'], raw[item]['time']))

    hours = filterTime()
    if hours == -1:
        return -2

    if len(hours) < 1:
        print("No data found")
        return -2

def loadConfig():
    try:
        global startTime
        global startDay
        global endTime
        global endDay
        global onDuration
        prop = open("properties.conf", "r")
        dat = json.loads(str(prop.read()))
        startTime = int(dat["starttime"])
        startDay = int(dat["startday"])
        endTime = int(dat["endtime"])
        endDay = int(dat["endday"])
        onDuration = int(dat["onhours"])
        prop.close()
        return 0
    except:
        return -1

def GetLowestWholeHours(lupd = None):
    lpRtn = loadConfig()
    if lpRtn == -1:
        return -5, -5, -5
    st = init()
    if st == -1:
        return -2, -2, -2
    elif st == -2:
        return -4, -4, -4
    # if lupd is not None:
    #     if datetime.datetime.strptime(str(raw['0.19']['time']).split(' ')[0], "%Y-%m-%d").date() == lupd.date():
    #         return -1, -1, -1
    try:
        return getLowestHours(calcPowerHours()), priceOfDay, datetime.datetime.strptime(str(raw['0.19']['time']).split(' ')[0], "%Y-%m-%d")
    except:
        return -3, -3, -3

# lowest = GetLowestWholeHours()
# print(GetLowestWholeHours())
# print(GetLowestSingleHours())asdasd