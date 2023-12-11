import time
import os
from datetime import datetime
from zoneinfo import ZoneInfo

if __name__ == "__main__":
    tz = ZoneInfo("America/Los_Angeles")
    currentTime = datetime.now(tz=tz)
    print(currentTime)
    hour = currentTime.hour
    weekday = currentTime.weekday()

    pause = True
    if "PAUSE" in os.environ:
        pause = (os.environ["PAUSE"] != "FALSE")

    if pause:
        print("Sending paused")

    if weekday == 1:
        print("Send notice test")
        cmd = "python3 sender.py notice"
        print(os.popen(cmd).read())
    elif weekday == 2:
        print("Send checkout test")
        cmd = "python3 sender.py checkout"
        print(os.popen(cmd).read())
    elif weekday == 4:
        print("Send notice test")
        cmd = "python3 sender.py notice"
        print(os.popen(cmd).read())
    elif weekday == 5:
        print("Send notice (Satureday)")
        cmd = "python3 sender.py notice" # send"
        if not pause:
            cmd += " send"
        print(os.popen(cmd).read())
    elif weekday == 6:
        print("Send checkout (Sunday)")
        cmd = "python3 sender.py checkout" # send"
        if not pause:
            cmd += " send"
        print(os.popen(cmd).read())
    else:
        print(f"Do nothing ({weekday})")

