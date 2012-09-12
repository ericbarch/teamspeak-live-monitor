import threading
import redis
import time
import socket
from json import loads, dumps

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def reformat(str):
    str = str.replace('\p', '|').replace('\\\\', '\\').replace('\\/', '/').replace('\s', ' ').replace('\t', '   ')
    str = "<br />".join(str.split("\n"))
    return str

def keepalive():
    while True:
        time.sleep(60)
        client_socket.send("servernotifyregister event=textchannel id=1\n")

def socketIO():
    client_socket.connect(("localhost", 10011))
    client_socket.send("login admin PASSWORD\nuse 1\nservernotifyregister event=textchannel id=1\n")
    clrdata = client_socket.recv(8192)
    threading.Thread(target=keepalive).start()
    while True:
        data = client_socket.recv(8192)
        if ("error id=0 msg=ok" not in data):
            arrSplit = data.split(' ')
            uName = reformat(arrSplit[4].replace("invokername=", ""))
            uMsg = reformat(arrSplit[2].replace("msg=", ""))
            uTime = round(time.time())
            msg = {'user': uName, 'msg': uMsg, 'time': uTime}
            r = redis.Redis(host='localhost', db=0)
            r.publish('ts', dumps(msg))
            r.rpush('msglog', dumps(msg))

if __name__ == "__main__":
     socketIO()
