#!/usr/bin/python3

import os
import time
import sys
import threading
import codecs
import json
from gmail3 import GMail
from datetime import datetime, timedelta
from mongodb import MongoDB
from zoneinfo import ZoneInfo

#os.chdir(sys.path[0])
#sys.path = ['../gserver'] + sys.path
from email_writer import EmailWriter

GOOGLE_ACCOUNT = "hkmcc.library@gmail.com"

global subject
global body
global msgType

def sendEmail(userList, test):
  count = 0
  tokenStr = os.environ["MAIL_TOKEN"]
  token = json.loads(tokenStr)
  gmail = GMail(token)
  logFile = open("emailLog.txt", "a", encoding="utf-8")
  logFile.write(str(datetime.now()) + str(test) + "\n")
  logFile.write("="*30 + "\n")
  for key in userList:
    user = userList[key]
    toaddr = user['email']
    print(f"Send {key} {toaddr}")

    if len(toaddr) == 0:
        continue
#    toaddr = "linupa1@gmail.com"
    fromaddr = GOOGLE_ACCOUNT
    sub = subject
    content = getBody(user)

    if verbose:
        print(sub)
        print(content)
    msg = gmail.CreateMessage(fromaddr, toaddr, sub, content)
    if not test:
        gmail.SendMessage(GOOGLE_ACCOUNT, msg)
    else:
        print("Skip sending")
    logFile.write(content + "\n")
    time.sleep(0.01)
    count += 1
#    if count > 5:
#        break;
  logFile.close()

if __name__ == '__main__':

  if len(sys.argv) < 2:
    exit(-1)

  msgTypes = {"notice": 0, "checkout": 1}
  msgType = sys.argv[1]
  if msgType not in msgTypes:
    exit(-1)

  test = True
  verbose = False
  if len(sys.argv) > 2:
      if sys.argv[2] == "send":
          test = False
      elif sys.argv[2] == "verbose":
          verbose = True

  if len(sys.argv) > 3:
      if sys.argv[3] == "send":
          test = False
      elif sys.argv[3] == "verbose":
          verbose = True

  print("Open MongoDB")
  password = os.environ["MONGODB_PASSWORD"]
  connection = 'mongodb+srv://linupa:{}@hkmcclibrary.s59ur1w.mongodb.net/?retryWrites=true&w=majority'.format(password)
  db = MongoDB(connection)


  print(f"Msg type: {msgType} Test:{test}")
  msgType = msgTypes[msgType]
  userList= dict()

  textFile =  open('text/text.json', 'r', encoding='utf-8')
  text = json.load(textFile)['kr']

  if msgType == 0:
      subject = text["courtesyNotice"]
      f2 = open('text/CourtesyNotice.txt', 'r', encoding='utf-8')
      body = f2.read()
      print(body)
  else:
      subject = text["rentalHistory"]
      f3 = open('text/CheckInOut.txt', 'r', encoding='utf-8')
      body = f3.read()
      print(body)

#  print(sys.path[1])
#  directory = sys.path[1]
#  os.chdir(sys.path[1])

  directory = os.getcwd()
  directory = sys.version

  previewIndex = 0

  def setReceiver(db, arg):
    tz = ZoneInfo("America/Los_Angeles")
    today = datetime.now(tz=tz).date()
    print(f"Today: {today}")
    if arg == 0:
        return db.getRecentDueDate(today, 6)
    else:
        return db.getRecentActivity(today, 6)

  def getBody(entry):
     writer = EmailWriter()
     txt = body
     context = {
        'user': {'id': entry['id'], 'name': entry['name']},
        'content': ""
     }
     if verbose:
         print(entry)

     if msgType == 0:
       writer = EmailWriter()
       rentList = ""
       for log in entry['rent']:
#         print(log)
         book = writer.Render("item.txt", log)
         rentList += book
       context.update({'content': rentList})
     elif msgType == 1:
       rentList = ""
       returnList = ""
       for log in entry['rent']:
#         print(log)
         book = writer.Render("book.txt", log)
         if log['log']["book_state"] == 0:
            returnList += book
         elif log['log']["book_state"] == 1:
            rentList += book
#       context.update(db.GetLogString(entry['rent']))
       context.update({'checkout': rentList, 'checkin': returnList })

     f = codecs.open('text/cache.txt', 'w', 'utf-8')
     f.write(txt);
     f.close()

     return writer.Render('cache.txt', context)

  userList = setReceiver(db, msgType)

  sendEmail(userList, test)

