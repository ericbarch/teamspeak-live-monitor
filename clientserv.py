import threading
import tornado.ioloop
import tornado.web
import tornadio
import tornadio.router
import tornadio.server
import redis
from json import loads, dumps

participants = set()

def redis_listener():
    rsub = redis.Redis(host='localhost', db=0)
    rsub.subscribe('ts')
    for m in rsub.listen():
        if m['type'] == 'message':
            for p in participants:
                p.send(loads(m['data']))

class ChatConnection(tornadio.SocketConnection):
    def on_open(self, *args, **kwargs):
        participants.add(self)
        print len(participants)

    def on_message(self, message):
        if (message == '!init'):
            rret = redis.Redis(host='localhost', db=0)
            msgList = rret.lrange('msglog', -300, -1)
            for i in range(0, len(msgList), 1):
                self.send(loads(msgList[i]))
            self.send({'user': '', 'msg': '!done', 'time': ''})

    def on_close(self):
        participants.remove(self)
        print len(participants)

ChatRouter = tornadio.get_router(ChatConnection)

application = tornado.web.Application(
    [ChatRouter.route()],
    enabled_protocols = ['websocket',
                         'xhr-multipart',
                         'xhr-polling']
)

if __name__ == "__main__":
    threading.Thread(target=redis_listener).start()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(9090)
    tornado.ioloop.IOLoop.instance().start()
