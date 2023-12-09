import os
from datetime import datetime, timedelta
from mongodb import MongoDB

if __name__ == '__main__':
    print(f"Date {datetime.now()}")
    try:
        password = os.environ["MONGODB_PASSWORD"]
        connection = 'mongodb+srv://linupa:{}@hkmcclibrary.s59ur1w.mongodb.net/?retryWrites=true&w=majority'.format(password)
        db = MongoDB(connection)
    except KeyError:
        print("Cannot find MongoDB credential")


