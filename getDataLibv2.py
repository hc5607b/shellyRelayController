import urllib.request
import json
from datetime import datetime, timedelta

class Hour:
    def __init__(self, day, hour, price, timestamp):
        self.day = day
        self.hour = hour
        self.price = price
        self.timestamp = timestamp

    def __repr__(self):
        return f"Timestamp({self.day}, {self.hour}, {self.price}, {self.timestamp})"

# returns hourly price infromation as array of Hour objects ordered by date
def loadPrices():
    # load data from server
    hget = ""
    ts = []

    try:
        hget = urllib.request.urlopen("https://elspotcontrol.netlify.app/spotprices-v01-FI.json")
    except:
        return -1
    if hget.getcode() != 200:
        return -1

    # load data as JSON and navigate to right place
    data = json.loads(hget.read())['hourly_prices']
    
    for item in data:
        ts.append(Hour(int(item.split('.')[0]), int(item.split('.')[1]), data[item]['price'], datetime.strptime(data[item]['time'].split('+')[0], '%Y-%m-%d %H:%M:%S')))

    return ts

# sorts list by price from lowest to highest
def sortByPrice(arr):
    return sorted(arr ,key=lambda x: x.price, reverse=False)

# filters array by given time values.
def applyTimeSection(arr, sDay, sHour, eDay, eHour):
    startID = -1
    endID = -1
    
    for i in range(0, len(arr)):
        if arr[i].day == sDay and arr[i].hour == sHour:
            startID = i
            continue
        if arr[i].day == eDay and arr[i].hour == eHour:
            endID = i
    
    if startID == -1 or endID == -1:
        return -1
    return arr[startID:endID]

# returns cheapest hours. time argument tells how many hours is needed. Calculates row by average
def getCheapestInRow(arr, time):
    lowest = 999999
    lowestStartId = -1

    for i in range(0, len(arr)-time+1):
        av = 0
        for j in range(0, time):
            av += arr[i+j].price
        av = av / time
        if av < lowest:
            lowest = av
            lowestStartId = i
    if lowestStartId == -1:
        return -1
    return arr[lowestStartId:lowestStartId+time]

# get single cheapest hours by amount
def getCheapest(arr, am):
    return sortByPrice(arr)[0:am]

# returns combined version. Format: start time, end time
def combineTimes(arr):
    rtn = []
    arr.sort(key=lambda x: x.timestamp, reverse=False)
    startTemp = -1
    for i in range(0, len(arr)):
        if startTemp == -1:
            startTemp = i
        if len(arr) - 1 == i or arr[i].timestamp + timedelta(hours=1) != arr[i+1].timestamp:
            rtn.append([arr[startTemp].timestamp.hour, (arr[i].timestamp + timedelta(hours=1)).hour])
            startTemp = -1
    return rtn
