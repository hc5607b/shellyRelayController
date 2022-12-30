import datetime
from enum import Enum
import smtplib
from email.message import EmailMessage

class LogType(Enum):
    INFO = 0,
    ERROR = 1,
    WARNING = 2

file = None

def openLog():
    global file
    file = open("log.txt", "a")

def closeLog():
    global file
    file.close()

def Print(dat, logType = LogType.INFO):
    global file
    msg = f"[{datetime.datetime.now()}] [{logType.name}] {str(dat)}"
    file.write(f"{msg}\n")
    print(f"{msg}")