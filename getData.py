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


log = open('/home/master/scripts/log.txt', 'a')
logForSite = ""

def writeLog(str):
    log.write(f"[{datetime.datetime.now()}] {str}\n")
    global logForSite
    logForSite = logForSite + f"[{datetime.datetime.now()}] {str}\n"

writeLog("Progarm started")

raw = json.loads(urllib.request.urlopen("https://elspotcontrol.netlify.app/spotprices-v01-FI.json").read())
raw = raw['hourly_prices']

priceOfDay = -1
hours = []

startTime = 23
startDay = 0
endTime = 7
endDay = 1
onDuration = 3

def filterTime():
    startID = 0
    endID = 0
    for i in range(0, len(hours)):
        if hours[i].day == startDay and hours[i].hour == startTime:
            startID = i
            continue
        if hours[i].day == endDay and hours[i].hour == endTime:
            endID = i
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
            lID = i-1
    global priceOfDay 
    priceOfDay = val
    onHours = []
    # print(lID)
    _start = startTime + lID
    if _start > 23:
        _start = _start - 23
    for i in range(0, 3):
        nTime = _start + i
        if nTime > 23:
            nTime = nTime - 23
        onHours.append(nTime)
    return onHours

def GetLowestWholeHours():
    return getLowestHours(calcPowerHours())

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

for item in raw:
    hours.append(Hour(int(item.split('.')[0]), int(item.split('.')[1]), raw[item]['price'], raw[item]['time']))

hours = filterTime()

if len(hours) < 1:
    print("No data found")
    exit()

lowest = GetLowestWholeHours()
writeLog(f"Price of day is {priceOfDay} at hours {lowest}")
# print(GetLowestSingleHours())
f = open('/var/www/html/power.json', 'a')
f.truncate(0)
f.write(str(formatToJSON(lowest)))
f.close()
writeLog("Power file updated")

writeLog("Bye!")
lf = open('/var/www/html/logfordata.txt', 'a')
lf.write(logForSite)
lf.close()

log.close()