import os
from sqsClient import SQSClient
from mongodb import MongoDB
from dbUtil import updateCloud, list2dict

if __name__ == "__main__":

    print("Open MongoDB")
    if "MONGODB_PASSWORD" in os.environ:
        password = os.environ["MONGODB_PASSWORD"]
    else:
        from config import Config
        password = Config["password"]
    connection = 'mongodb+srv://linupa:{}@hkmcclibrary.s59ur1w.mongodb.net/?retryWrites=true&w=majority'.format(password)
    db = MongoDB(connection)

    client = SQSClient()
    msgs = client.PopQueue()

    print(db.mdRequest)

    reqToCheck = dict()
    for key in db.mdRequest:
        req = db.mdRequest[key]
        if req['state'] != 'pending' or 'book_id' not in req:
            continue
        userId = req['user_id']
        bookId = req['book_id']
        if userId in reqToCheck:
            reqToCheck[userId].add(bookId)
        else:
            reqToCheck[userId] = {bookId}
    print(reqToCheck)
    msgDict = dict()
    for msg in msgs:
        userId = msg['user_id']
        bookId = msg['book_id']
        if userId in reqToCheck:
            if bookId in reqToCheck[userId]:
                print('Duplicate request')
                print(msg)
                print(reqToCheck)
                continue
            else:
                reqToCheck[userId].add(bookId)
        else:
            reqToCheck[userId] = {bookId}
        msg['state'] = 'pending'
        msgDict[msg['_id']] = msg



    print(msgDict)

    updateCloud([list(msgDict.keys()), list(), list()], msgDict, db.requestDb)





