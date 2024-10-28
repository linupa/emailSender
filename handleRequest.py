import os
from mongodb import MongoDB
from dbUtil import *
import subprocess
import datetime
from gsheet import GSheet
import json

class Request:
    def __init__(self, db):
        self.db = db

        self.readDb()

    def readDb(self):
        print("="*80)
        print("Download library DB")

        print("="*80)
        print("Book")
        self.books = self.db.mdBooks
        print(f"{len(self.books)} books")

        print("="*80)
        print("User")
        self.users = self.db.mdUsers
        print(f"{len(self.users)} users")

        print("="*80)
        print("Rent")
        self.rents = self.db.mdRent
        print(f"{len(self.rents)} rents")

        print("="*80)
        print("Request")
        self.requests = self.db.mdRequest
        print(f"{len(self.requests)} requests")

    def extend(self):
        print("="*80)
        print(f"Check requests for extend")
        retRequest = list()
        retBookSeq = list()
        for key in self.requests:
            request = self.requests[key]
            if request["action"] != "extend":
                continue
            if request["state"] != "pending":
                continue
            print(request)
            bookId = request["book_id"]
            retRequest.append(key)
            if bookId not in self.books:
                print(f"Unknown book ID: {bookId}")
                request["state"] = "rejected"
                continue
            seq = self.books[bookId]["seqnum"]
            if seq not in self.rents:
                print(f"Unknown seq number: {seq}")
                for rentKey in self.rents:
                    rent = self.rents[rentKey]
                    if rent["book_id"] == bookId:
                        print(f"Found book in {rent}")
                request["state"] = "rejected"
                continue
            rent = self.rents[seq]
            print(rent)
            if rent["book_id"] != bookId or rent["user_id"] != request["user_id"]:
                print(f"Rent info does not match {rent}")
            print(f"Extend due date {rent['return_date']} for {bookId}")
            dueDate = datetime.datetime.strptime(rent["return_date"], "%Y-%m-%d")
            print(dueDate)
            now = datetime.datetime.now()
            refDate = now if now > dueDate else dueDate
            newRetDate = timeToString(refDate + datetime.timedelta(days=21), True)
            print(f"New due date {newRetDate}")
            request["state"] = "done"
            rent["return_date"] = newRetDate
            rent["extend_count"] += 1
            retBookSeq.append(seq)
        return [retRequest, retBookSeq]


    def bookRequest(self):
        print("="*80)
        print(f"Check requests for book request")
        ret = list()
        for key in self.requests:
            request = self.requests[key]
            if request["action"] != "bookRequest":
                continue
            if request["state"] != "pending":
                continue
            ret.append(request)
        return ret

if __name__ == '__main__':
    # Open MongoDB
    if "GITHUB_ACTIONS" in os.environ:
        password = os.environ["MONGODB_PASSWORD"]
    else:
        from config import Config
        password = Config['password']
#    SHEET_ID="1ahHXLb87hsnqzyo6IP7WLTVgt_Ra91RxUhZZVOcYU_M"
    SHEET_ID="1aWzA4jlcCZGAeMa2L997ptiokA_Kt0TeRsZnt6khMbM"
    #sheetId = os.environ["SHEET_ID"]
    sheetId = SHEET_ID
    connection = 'mongodb+srv://linupa:{}@hkmcclibrary.s59ur1w.mongodb.net/?retryWrites=true&w=majority'.format(password)
    db = MongoDB(connection)

    with open("text.json", "r") as f:
        text = json.load(f)

    request = Request(db)

    changedRequest, changedRent = request.extend()


    sheet = GSheet()

    print(changedRequest)
    for key in changedRequest:
        bookRequest = request.requests[key]
        print(bookRequest)

    print(changedRent)
    for key in changedRent:
        print(request.rents[key])

    bookRequests = request.bookRequest()

#    labels = sheet.get(sheetId, f"BookRequest!A1:Z1")[0]
    lines = sheet.get(sheetId, f"A2:Z3")
    labelIdx = dict()
    maxColumn = 0
    for labels in lines:
        for i in range(len(labels)):
            label = labels[i].lower().strip()
            if len(label) > 0:
                labelIdx[label] = i
            if i > maxColumn:
                maxColumn = i;
    print(f"Label {labelIdx}")

    BATCH_SIZE = 100
    oldRequests = list()
    lastRow = 4
    oldIds = dict()
    lastEntry = 1
    titleIdx = labelIdx[text["title"]]
    idIdx = labelIdx[text["id"]]
    stateIdx = labelIdx[text["state"]]
    while True:
#        values = sheet.get(sheetId, f"BookRequest!A{lastRow}:Z{lastRow+BATCH_SIZE}")
        values = sheet.get(sheetId, f"A{lastRow}:Z{lastRow+BATCH_SIZE}")
        added = False
        for idx in range(len(values)):
            value = values[idx]
            if len(value) < titleIdx or value[titleIdx] == "":
                print(f"Empty row: {lastRow + idx}")
                continue
            lastEntry = lastRow + idx
            oldRequests.append(value)
            if len(value) > idIdx and len(value[idIdx]) > 0:
                oldIds[value[idIdx]] = value[stateIdx] if len(value) > stateIdx else ""
            added = True
        lastRow += len(values)
        if len(values) < BATCH_SIZE:
            break
        if added == 0:
            break

    print(f"Read {len(oldRequests)} requests")

    idx = lastEntry + 1
    added = 0
    for bookRequest in bookRequests:
        reqId = bookRequest['_id']
        date = datetime.datetime.strptime(bookRequest["date"], "%Y-%m-%d")
        if reqId in oldIds:
            if oldIds[reqId] == "done":
                bookRequest["state"] = "done"
                changedRequest.append(reqId)
            continue
        userId = bookRequest["user_id"]
        if userId in request.users:
            name = request.users[userId]["name"]
        else:
            name = ""
        print(date)
        print(date.strftime("%m/%d/%Y"))
        data = [None] * (maxColumn + 1)
        entry = dict()
        entry[text["id"]] = reqId
        entry[text["date"]] = date.strftime("%m/%d/%Y")
        entry[text["requester"]] = userId
        entry[text["name"]] = name
        entry[text["title"]] = bookRequest["title"]
        entry[text["author"]] = bookRequest["author"]
        entry[text["publisher"]] = bookRequest["publisher"]
        entry[text["note"]] = bookRequest["note"]
        for label in labelIdx:
            if label not in entry or label not in labelIdx:
                continue
            i = labelIdx[label]
            data[i] = entry[label]

#        sheet.update(sheetId, f"BookRequest!A{idx}:Z{idx}", [data])
        sheet.update(sheetId, f"A{idx}:Z{idx}", [data])
        added += 1
        idx += 1
    print(f"{added} requests added")

    updateCloud([list(), changedRequest, list()], request.requests, db.requestDb)
    updateCloud([list(), changedRent, list()], request.rents, db.rentDb)
