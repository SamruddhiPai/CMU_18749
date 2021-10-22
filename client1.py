#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import time
from util import log

CONN_ID = 1
s1_sel = selectors.DefaultSelector()
s2_sel = selectors.DefaultSelector()
num_conns = CONN_ID
host1, port1 = '127.0.0.1', 1234
host2, port2 = '172.26.78.32', 14064

class Client:

    def __init__(self,host,port,sel):
        self.host = host
        self.port = port
        self.sel = sel

    def start_connections(self):
        server_addr = (self.host, self.port)
        connid = CONN_ID
        print("starting connection", connid, "to", server_addr)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.connect_ex(server_addr)
        self.events = selectors.EVENT_READ | selectors.EVENT_WRITE
        #events = selectors.EVENT_WRITE
        self.sel.register(self.sock, self.events, data=None)

    def service_connection(self, key, mask, data):
        self.sock = key.fileobj
        #data = key.data
        if mask & selectors.EVENT_READ:
            self.recv_data = self.sock.recv(1024)  # Should be ready to read
            if self.recv_data:
                receive_str = "Received " + str(repr(self.recv_data)) + " from connection " + str(data.connid)
                # print()
                log(receive_str)
                data.recv_total += len(self.recv_data)
            if not self.recv_data or data.recv_total == data.msg_total:
                #print("closing connection", data.connid)
                self.sel.unregister(self.sock)
                #sock.close()
        if mask & selectors.EVENT_WRITE:
            if not data.outb and data.messages:
                data.outb = data.messages.pop(0)
            if data.outb:
                #print("sending", repr(data.outb), "to connection", data.connid)
                req_str = "Sending " + str(repr(data.outb)) + " to Server " + str(self.host) + ":" + str(self.port)
                log(req_str)
                self.sent = self.sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[self.sent:]


# if __name__=='main':

c1_s1 = Client(host1,port1,s1_sel)
c1_s2 = Client(host2,port2,s2_sel)
c1_s1.start_connections()
c1_s2.start_connections()

try: 
    while True:
        events1 = s1_sel.select(timeout=1)
        events2 = s2_sel.select(timeout=1)
        header_type = "REQ;"
        header_message = "from client: " + str(CONN_ID) + ";"
        messages = "" + header_type + header_message
        if events1[0][-1] != 1 and events2[0][-1] != 1:  # writing data - mask != 1
            log("Enter a number:")
            header_data = input()
            messages = messages + header_data + ";"
            messages = [bytes(messages, 'utf-8')]
            data1 = types.SimpleNamespace(
                connid=CONN_ID,
                msg_total=1024,
                recv_total=0,
                messages=list(messages),
                outb=b"",
            )
            
            data2 = types.SimpleNamespace(
                connid=CONN_ID,
                msg_total=1024,
                recv_total=0,
                messages=list(messages),
                outb=b"",
            )

            for key, mask in events1:
                # print('Event1 before\n',events1)
                c1_s1.service_connection(key, mask, data1)
                s1_sel.modify(key.fileobj, selectors.EVENT_READ, data=None)
                events1 = s1_sel.select(timeout=1)
                # print('Event1 after\n',events1)
            # print('outside 1st for loop')
            
            for key, mask in events2:
                c1_s2.service_connection(key, mask, data2)
                s2_sel.modify(key.fileobj, selectors.EVENT_READ, data=None)
                events2 = s2_sel.select(timeout=1)
                
        else:
            # print('in else')
            data1 = types.SimpleNamespace(
            connid=CONN_ID,
            msg_total=1024,
            recv_total=0,
            outb=b"",
        ) 
            data2 = types.SimpleNamespace(
            connid=CONN_ID,
            msg_total=1024,
            recv_total=0,
            outb=b"",
        ) 
        for key, mask in events1:
            c1_s1.service_connection(key, mask, data1)
            s1_sel.modify(key.fileobj, selectors.EVENT_READ | selectors.EVENT_WRITE , data=None)
            events1 = s1_sel.select(timeout=1)
        
        for key, mask in events2:
            c1_s2.service_connection(key, mask, data2)
            s2_sel.modify(key.fileobj, selectors.EVENT_READ | selectors.EVENT_WRITE , data=None)
            events2 = s2_sel.select(timeout=1)

    
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    s1_sel.close()
    s2_sel.close()