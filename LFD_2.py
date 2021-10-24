#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import time, errno
from util import log
from threading import Thread

class LFD_client(Thread):
    def __init__(self,host,port,sel):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.sel = sel

    def start_connections(self,host, port):
        server_addr = (host, port)
        connid = 2
        print("Starting connection", connid, "to", server_addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        # events = selectors.EVENT_WRITE
        self.sel.register(sock, events, data=None)

    def service_connection(self,key, mask, data):
        sock = key.fileobj
        #data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                receive_str = "Received " + str(repr(recv_data)) + " from Server"
                log(receive_str)
                data.recv_total += len(recv_data)
            if not recv_data or data.recv_total == data.msg_total:
                close_message = "Closing Connection " + str(data.connid)
                log(close_message)
                self.sel.unregister(sock)
                #sock.close()
        if mask & selectors.EVENT_WRITE:
            if not data.outb and data.messages:
                data.outb = data.messages.pop(0)
            if data.outb:
                send_message = "Sending " + str(repr(data.outb)) + " to Server"
                log(send_message)
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]
    def run(self):
        server_found = str(input("Server on. LFD on? : "))
        if (server_found == 'y' or server_found == 'Y'):
            self.start_connections(self.host, int(self.port))
            try:
                while True:
                    messages = 'Are you alive?'
                    messages = [bytes(messages, 'utf-8')]
                    data = types.SimpleNamespace(
                        connid=CONN_ID,
                        msg_total=1024,
                        recv_total=0,
                        messages=list(messages),
                        outb=b"",
                    )
                    events = self.sel.select(timeout=1)
                    if events:
                        for key, mask in events:
                            self.service_connection(key, mask, data)
                    time.sleep(heart_beat)

            except IOError as e:
                close_message = "Server got disconnected"
                log(close_message)
                    
            except KeyboardInterrupt:
                print("caught keyboard interrupt, exiting")



# LFD AS SERVER
class LFD_server(Thread):
    def __init__(self,host,port,sel):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.sel = sel

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        #events = selectors.EVENT_READ
        self.sel.register(conn, events, data=data)

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            try:
                recv_data = sock.recv(1024)  # Should be ready to read
                if recv_data:
                    recv_data_str = str(recv_data)
                    datalist = recv_data_str.split(";")
                    try:
                        req_type = datalist[0]
                        req_message = datalist[1]
                        req_str = "REQ: " + str(repr(datalist))
                        log(req_str)
                        num = datalist[2]
                        log(update)
                        print("------")
                        data.outb = b'Acknowledgement'
                        print('Updated data.outb')
                        
                    except:
                        if (str(recv_data_str) == "b'I am a server and I am up.'"):
                            server_found = True
                            log("Server detected")
                            data.outb = b'Server detected.'

                else:
                    log(("Closing connection to " + str(data.addr)))
                    self.sel.unregister(sock)
                    sock.close()
            except:
                log("No response from server.")
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:] #to clear data.outb
    
    def run(self):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((self.host, self.port))
        lsock.listen()
        # print("\nListening on", (self.host, self.port))
        lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)
        try:
            while True:
                events = self.sel.select(timeout=None) # Blocks until client ready for I/O, in effect till client sends data
                # print(events)
                for key, mask in events:
                    if key.data is None: # key.data opaque class, will be assigned to ceratin type by client(ex: types.SimpleNamespace)
                        self.accept_wrapper(key.fileobj)
                    else:
                        self.service_connection(key, mask)
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.sel.close()


    

server_found = False

heart_beat = float(input('\n\nEnter heart beat frequency (in seconds): '))

#LFD AS SERVER
CONN_ID = 10
sel_server = selectors.DefaultSelector()
host_s, port_s, num_conns = '127.0.0.1', 1235, 1
lfd_server = LFD_server(host_s, port_s, sel_server)
lfd_server.start()

# LFD AS CLIENT
# heart_beat = None
# CONN_ID = 10
# sel_client = selectors.DefaultSelector()
# host_c, port_c, num_conns = '127.0.0.1', 1234, 1

# lfd_client = LFD_client(host_c, port_c, sel_client)
# lfd_client.start()

