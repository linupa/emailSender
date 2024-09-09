import os
from mongodb import MongoDB
from dbUtil import *
import subprocess
import datetime

class Extend:
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
        print(f"Check requests")
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

if __name__ == '__main__':
    # Open MongoDB
    if "GITHUB_ACTIONS" in os.environ:
        password = os.environ["MONGODB_PASSWORD"]
    else:
        from config import Config
        password = Config['password']
    connection = 'mongodb+srv://linupa:{}@hkmcclibrary.s59ur1w.mongodb.net/?retryWrites=true&w=majority'.format(password)
    db = MongoDB(connection)

    extend = Extend(db)

    changedRequest, changedRent = extend.extend()

    print(changedRequest)
    for key in changedRequest:
        print(extend.requests[key])

    print(changedRent)
    for key in changedRent:
        print(extend.rents[key])

    updateCloud([list(), changedRequest, list()], extend.requests, db.requestDb)
    updateCloud([list(), changedRent, list()], extend.rents, db.rentDb)
