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
import argparse

#os.chdir(sys.path[0])
#sys.path = ['../gserver'] + sys.path
from email_writer import EmailWriter

GOOGLE_ACCOUNT = "hkmcc.library@gmail.com"

global subject
global body
global msgType

def sendEmail(userList, test):
  count = 0
  print(f"Test {test}")
  tokenStr = None
  if "MAIL_TOKEN" in os.environ:
    tokenStr = os.environ["MAIL_TOKEN"]
  else:
    print("MAIL TOKEN does not exist")
    KEY="credentials.json"
    if os.path.isfile(KEY):
        with open(KEY, "r") as f:
            tokenStr = f.read()
  if tokenStr:
      token = json.loads(tokenStr)
  else:
      token = None
  gmail = GMail(token)
  logFile = open("emailLog.txt", "a", encoding="utf-8")
  logFile.write(str(datetime.now()) + str(test) + "\n")
  logFile.write("="*30 + "\n")
  for key in userList:
    user = userList[key]
    toaddr = user['email'].strip()
    print(f"Send {key} {toaddr}")

    if len(toaddr) == 0:
        continue
    try:
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
    except Exception as e:
        print(f"Exception while mail send ({e})")
  logFile.close()

if __name__ == '__main__':

  parser = argparse.ArgumentParser(prog='emailSensor')
  parser.add_argument('-t', '--type')
  parser.add_argument('-d', '--debug', action='store_true')
  parser.add_argument('-v', '--verbose', action='store_true')
  parser.add_argument('-s', '--send', action='store_true')
  parser.add_argument('-m', '--msg')

  args = parser.parse_args()

  if args.type == None:
    parser.print_help()
    exit(-1)

  msgTypes = {"notice": 0, "checkout": 1, "all": 2}
  msgType = args.type
  if msgType not in msgTypes:
    print("Invalid msg type")
    parser.print_help()
    exit(-1)

  test = not args.send
  verbose = args.verbose

  print("Open MongoDB")
  if "MONGODB_PASSWORD" in os.environ:
    password = os.environ["MONGODB_PASSWORD"]
  else:
    from config import Config
    password = Config["password"]
  connection = 'mongodb+srv://linupa:{}@hkmcclibrary.s59ur1w.mongodb.net/?retryWrites=true&w=majority'.format(password)
  db = MongoDB(connection)

  print(f"Msg type: {msgType} Test:{test}")
  msgType = msgTypes[msgType]
  userList= dict()

  if msgType == 2 and args.msg == None:
    print("msg type is all, but no msg")
    exit(-1)

  textFile =  open('text/text.json', 'r', encoding='utf-8')
  text = json.load(textFile)['kr']

  if msgType == 0:
      subject = text["courtesyNotice"]
      f2 = open('text/CourtesyNotice.txt', 'r', encoding='utf-8')
      body = f2.read()
  elif msgType == 1:
      subject = text["rentalHistory"]
      f3 = open('text/CheckInOut.txt', 'r', encoding='utf-8')
      body = f3.read()
  elif msgType == 2:
    with open(args.msg, 'r', encoding='utf-8') as f:
        text = json.load(f)
        subject = text['title']
        body = text['contents']
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
    elif arg == 1:
        return db.getRecentActivity(today, 6)
    elif arg == 2:
        return db.getAllUsers()

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

#  userList = {'AB0354': {'id': 'AB0354', 'email' : 'linupa@gmail.com', 'name': 'Name'}}

  sendEmail(userList, test)

