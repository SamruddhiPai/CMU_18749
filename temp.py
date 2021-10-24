from socket import *
from threading import Thread

class Server(Thread):
    def __init__(self,host,port,name):
        Thread.__init__(self)
        self.port = port
        self.host = host
        self.name = name
        self.bufsize = 1024
        self.addr = (host,port)

        self.socket = socket(AF_INET , SOCK_STREAM)
        self.socket.bind(self.addr)

    def run(self):
        self.socket.listen(5)
        while True:
            print('Waiting for connection..')
            client, caddr = self.socket.accept()
            print('Connected To',caddr)

            data = client.recv(self.bufsize)
            if not data:
                continue
            print(data)


class Client(Thread):
    def __init__(self,host,port,name):
        Thread.__init__(self)
        self.port = port
        self.host = host
        self.name = name
        self.bufsize = 1024
        self.addr = (host,port)

        self.socket = socket(AF_INET , SOCK_STREAM)

    def run(self):
        invalid = True
        while invalid:
            try:
                invalid = False
                self.socket.connect(self.addr)
            except:
                invalid = True

        while True:
            data = input('> ')
            if not data:
                continue
            data = name+' said : '+data

host = ''
p1 = int(input('Enter Port 1 : '))
p2 = int(input('Enter Port 2 : '))
name = input('Enter Your Name: ').strip()


server = Server(host,p2,name)
client = Client(host,p1,name)

server.start()
client.start()

server.join()