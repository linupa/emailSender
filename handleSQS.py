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

    print("Receive requests")
    REGION = "us-west-1"
    URL = "https://sqs.us-west-1.amazonaws.com/088564131385/HKMCCLibraryRequest.fifo"
    if "ACCESS_KEY" in os.environ:
        ACCESS_KEY = os.environ["ACCESS_KEY"]
    else:
        from config import Config
        ACCESS_KEY = Config["access_key"]

    if "SECRET_ACCESS_KEY" in os.environ:
        SECRET_ACCESS_KEY = os.environ["SECRET_ACCESS_KEY"]
    else:
        SECRET_ACCESS_KEY = Config["secret_access_key"]
    sqsConfig = {
        "REGION": REGION,
        "URL": URL,
        "ACCESS_KEY": ACCESS_KEY,
        "SECRET_ACCESS_KEY": SECRET_ACCESS_KEY
    }
    client = SQSClient(sqsConfig)
    msgs = client.PopQueue()

    print(db.mdRequest)

    reqToCheck = dict()
    for key in db.mdRequest:
        req = db.mdRequest[key]
        if req['state'] != 'pending':
            continue
        if req['action'] == 'extend':
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
        if req['action'] == 'extend':
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

