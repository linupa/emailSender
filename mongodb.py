from pymongo import MongoClient
from datetime import datetime, timedelta


class MongoDB:
    def __init__(self, connection):
        self.client = MongoClient(connection)

        db = self.client.library
        bookDb = db.book
        self.mdBooks = dict()
        for book in bookDb.find():
            key = book['_id']
            self.mdBooks[key] = book
        print(f"Book len {len(self.mdBooks)}")

        userDb = db.user
        self.mdUsers = dict()
        for user in userDb.find():
            key = user['_id']
            self.mdUsers[key] = user
        print(f"User len {len(self.mdUsers)}")

        rentLogDb = db.rentLog
        self.mdRentLog = dict()
        for log in rentLogDb.find():
            key = log['_id']
            self.mdRentLog[key] = log
        print(f"rentLog len {len(self.mdRentLog)}")

        self.rentDb = db.rent
        self.mdRent = dict()
        for rent in self.rentDb.find():
            key = rent['_id']
            self.mdRent[key] = rent
        print(f"rent len {len(self.mdRent)}")

        self.requestDb = db.request
        self.mdRequest = dict()
        for request in self.requestDb.find():
            key = request['_id']
            self.mdRequest[key] = request
        print(f"request len {len(self.mdRequest)}")

    def getRecentDueDate(self, today, interval):
        userList = dict()
        refDate = str(today + timedelta(days= interval))
        print(f"Get recent due data ref: {refDate}")
        for key in self.mdRent:
            rent = self.mdRent[key]
            if rent["state"] not in {1, 3}:
                continue
            dueDate = rent["return_date"]
            if refDate < dueDate:
                continue
            user = rent["user_id"]
            book = rent["book_id"]
            if user in userList:
                userList[user]["rent"].append({'book': self.mdBooks[book], 'rent': rent})
            else:
                userInfo = dict()
                mdUser = self.mdUsers[user]
                userInfo["id"] = mdUser["_id"]
                userInfo["email"] = mdUser["email"]
                userInfo["name"] = mdUser["name"]
                userInfo["rent"] = [{'book': self.mdBooks[book], 'rent': rent}]
                userList[user] = userInfo

        print(f"Found {len(userList)} users")
        return userList

    def getRecentActivity(self, today, interval):
        userList = dict()
        refDate = str(today - timedelta(days= interval))
        todayDate = str(today)
        print(f"Get recent activity ref: {refDate}")
        for key in self.mdRentLog:
            rent = self.mdRentLog[key]
            if rent["book_state"] not in {0, 1}:
                continue
            date = rent["timestamp"].split(" ")[0]

            if date < refDate or date > todayDate:
                continue

            user = rent["user_id"]
            book = rent["book_id"]
            if user in userList:
                userList[user]["rent"].append({'book': self.mdBooks[book], 'log': rent})
            else:
                userInfo = dict()
                mdUser = self.mdUsers[user]
                userInfo["id"] = mdUser["_id"]
                userInfo["email"] = mdUser["email"]
                userInfo["name"] = mdUser["name"]
                userInfo["rent"] = [{'book': self.mdBooks[book], 'log': rent}]
                userList[user] = userInfo

        print(f"Found {len(userList)} users")

        return userList

    def getAllUsers(self):
        userList = dict()
        print(f"Get all users")
        for key in self.mdUsers:
            mdUser = self.mdUsers[key]

            userInfo = dict()
            userInfo["id"] = mdUser["_id"]
            userInfo["email"] = mdUser["email"]
            userInfo["name"] = mdUser["name"]
            userList[key] = userInfo

        print(f"Found {len(userList)} users")

        return userList
