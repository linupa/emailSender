import time
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--daily', action='store_true')
    parser.add_argument('-H', '--hourly', action='store_true')

    args = parser.parse_args()

    print(args)

    tz = ZoneInfo("America/Los_Angeles")
    currentTime = datetime.now(tz=tz)
    hour = currentTime.hour
    weekday = currentTime.weekday()
    weekdays = ["Mon", "Tue", "Wed", "Thr", "Fri", "Sat", "Sun"]
    print(f"{currentTime} {weekdays[weekday]}")

    print("Check SQS")
    cmd = "python3 handleSQS.py"
    print(os.popen(cmd).read())

    print("Handle Requests")
    cmd = "python3 handleRequest.py"
    print(os.popen(cmd).read())

    pause = True
    if "PAUSE" in os.environ:
        pause = (os.environ["PAUSE"] != "FALSE")

    if args.hourly or not args.daily:
        pause = True

    if pause:
        print("Sending paused")

    if weekday == 1:
        print("Send notice test (Tuesday)")
        cmd = "python3 sender.py --type notice"
        print(os.popen(cmd).read())
    elif weekday == 2:
        print("Send checkout test (Wednesday)")
        cmd = "python3 sender.py --type checkout"
        print(os.popen(cmd).read())
    elif weekday == 4:
        print("Send notice test (Friday)")
        cmd = "python3 sender.py --type notice"
        print(os.popen(cmd).read())
    elif weekday == 5:
        print("Send notice (Satureday)")
        cmd = "python3 sender.py --type notice" # send"
        if not pause:
            cmd += " --send"
        print(os.popen(cmd).read())
    elif weekday == 6:
        print("Send checkout (Sunday)")
        cmd = "python3 sender.py --type checkout" # send"
        if not pause:
            cmd += " --send"
        print(os.popen(cmd).read())
    else:
        print(f"Do nothing {weekdays[weekday]}({weekday})")

