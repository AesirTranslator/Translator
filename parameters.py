import json
import os
import random

print(random.randint(0, 10000))

MAX_START_ARGUMENT = 3
INDICATOR_PID_PATH = "/tmp/aesirindicator.tmp"
SOFTWARE_THREAD_CHECK_TIMEOUT = 6
SOFTWARE_UPDATER_TIMEOUT = 1
APPINDICATOR_ID = 'aesirIndicator'
CONF_FILE_PATH = os.path.dirname(__file__) + "/confs/conf.json"
CONF_FILE_INSTANCE = json.loads(open(CONF_FILE_PATH).read())
ICON_PATH = os.path.dirname(__file__) + CONF_FILE_INSTANCE["icons"]["folder"]


def notifySystem( title, message):
    try:
        os.system('notify-send "{}" "{}"'.format(title, message))
    except Exception as e:
        print(e)


def returnIconPath(icon):
    print(ICON_PATH + "/" + CONF_FILE_INSTANCE["icons"][icon])
    return ICON_PATH + "/" + CONF_FILE_INSTANCE["icons"][icon]


def returnTempDirectoryAndFile():
    return "/tmp/translator/", str(random.randint(0, 10000))


try:
    import httplib
except:
    import http.client as httplib


def have_internet():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False
