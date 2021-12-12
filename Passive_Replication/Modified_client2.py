#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import time
from util import log
import config


def get_status():
    f = open("out.txt", "r")
    temp = f.read()
    f.close()
    return temp

CONN_ID = 1
s1_sel = selectors.DefaultSelector()
s2_sel = selectors.DefaultSelector()
s3_sel = selectors.DefaultSelector()
GFD_sel = selectors.DefaultSelector()
num_conns = CONN_ID
host1, port1 = config.server_1_ip,config.server_1_listen
# host2, port2 = '172.26.78.32',14064
host2, port2 = config.server_2_ip,config.server_2_listen

host3, port3 = config.server_3_ip,config.server_3_listen

host, port = config.gfd_ip, config.gfd_listen

class Client:

    def __init__(self,host,port,sel, replicaID):
        self.host = host
        self.port = port
        self.sel = sel
        self.output = ""
        self.replicaID = replicaID

    def start_connections(self):
        server_addr = (self.host, self.port)
        connid = CONN_ID
        print("starting connection", connid, "to", server_addr)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.connect_ex(server_addr)
        #self.events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.events = selectors.EVENT_WRITE
        self.sel.register(self.sock, self.events, data=None)

    def service_connection(self, key, mask, data):
        self.sock = key.fileobj
        #data = key.data
        if mask & selectors.EVENT_READ:
            self.recv_data = self.sock.recv(1024)  # Should be ready to read
            if self.recv_data:
                if c1_s1.output != "" or c1_s2.output != "" or c1_s2.output != "":
                    receive_str = "Discarded Duplicate reply from " + self.replicaID
                else:
                    receive_str = "Received " + str(repr(self.recv_data)) + " from connection " + str(data.connid)
                # print()
                self.output = receive_str
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

class GFD:
    def __init__(self,host,port,sel):
        self.host = host
        self.port = port
        self.sel = sel
        self.s1 = 1
        self.s2 = 1
        self.s3 = 1
        self.flag1 = None
        self.flag2 = None
        self.flag3 = None

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
                recv_data_str = str(repr(recv_data))
                arr = ["S1", "S2", "S3"]
                str_temp = ""
                for serv in arr:
                    if (serv in recv_data_str):
                        str_temp += serv + "+"
                
                print("RECV MEMB", recv_data_str)
                print("STR TEMP", str_temp)
                if "S1" not in str_temp:
                    self.s1 = 0
                    self.flag1 = 0
                else:
                    if self.flag1 == 0:
                        print("CHANGING FLAG to 1")
                        self.flag1 = 1
                    self.s1 = 1
                if "S2" not in str_temp:
                    self.s2 = 0
                    self.flag2 = 0
                else:
                    self.s2 = 1
                    if self.flag2 == 0:
                        self.flag2 = 1
                if "S3" not in str_temp:
                    self.s3 = 0
                    self.flag3 = 0
                else:
                    if self.flag3 == 0:
                        self.flag3 = 1
                    self.s3 = 1

                # print(self.s1)
                # print(self.s2)
                # print(self.s3)
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
        try:
            for i in range(3):
                messages = 'Send me the Status'
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
                time.sleep(1)

        except IOError as e:
            close_message = "Server got disconnected"
            log(close_message)
                
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
# if __name__=='main':

c1_s1 = Client(host1,port1,s1_sel, "S1")
c1_s2 = Client(host2,port2,s2_sel, "S2")
c1_s3 = Client(host2,port3,s3_sel, "S3")
c1_GFD = GFD(host, port, GFD_sel)
c1_s1.start_connections()
c1_s2.start_connections()
c1_s3.start_connections()
c1_GFD.start_connections(host, int(port))

try: 
    while True:
        log("Enter a number:")
        header_data = input()
        c1_GFD.run()
        header_type = "REQ;"
        header_message = "from client: " + str(CONN_ID) + ";"
        messages = "" + header_type + header_message
        messages = messages + header_data + ";"
        messages = [bytes(messages, 'utf-8')]
        primary_status = get_status()
        for i in range(2):
            if primary_status == "S1" and c1_GFD.s1:
                # events1 = s1_sel.select(timeout=1)
                # print('Events 1', events1)
                if c1_GFD.flag1 == 1:
                    print("Flag 1 GFD!!!!!!!!!!!!!!")
                    s1_sel.close()
                    s1_sel = selectors.DefaultSelector()
                    c1_s1 = Client(host1,port1,s1_sel, "S1")
                    c1_s1.start_connections()   
                    c1_GFD.flag1 = None
                events1 = s1_sel.select(timeout=1)
                # print('Events 1', events1)
                if events1[0][-1] != 1:  # writing data - mask != 1
                    data1 = types.SimpleNamespace(
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
                else:
                    # print('in else')
                    data1 = types.SimpleNamespace(
                    connid=CONN_ID,
                    msg_total=1024,
                    recv_total=0,
                    outb=b"",
                    ) 
                    for key, mask in events1:
                        # print('Event1 before\n',events1)
                        c1_s1.service_connection(key, mask, data1)
                        #s1_sel.modify(key.fileobj, selectors.EVENT_READ|selectors.EVENT_WRITE, data=None)
                        s1_sel.modify(key.fileobj, selectors.EVENT_WRITE , data=None)
                        events1 = s1_sel.select(timeout=1)
            if primary_status == "S2" and c1_GFD.s2:
                # events2 = s2_sel.select(timeout=1)
                # print('Events2', events2)
                if c1_GFD.flag2 == 1:
                    print("Flag 2 GFD!!!!!!!!!!!!!!")
                    s2_sel.close()
                    s2_sel = selectors.DefaultSelector()
                    c1_s2 = Client(host2,port2,s2_sel, "S2")
                    c1_s2.start_connections()
                    c1_GFD.flag2 = None
                events2 = s2_sel.select(timeout=1)
                # print('Events2', events2)
                if events2[0][-1] != 1:  # writing data - mask != 1
                    # messages = messages + header_data + ";"
                    # messages = [bytes(messages, 'utf-8')]
                    data2 = types.SimpleNamespace(
                        connid=CONN_ID,
                        msg_total=1024,
                        recv_total=0,
                        messages=list(messages),
                        outb=b"",
                    )
                    for key, mask in events2:
                        c1_s2.service_connection(key, mask, data2)
                        s2_sel.modify(key.fileobj, selectors.EVENT_READ, data=None)
                        events2 = s2_sel.select(timeout=1)
                else:
                    data2 = types.SimpleNamespace(
                    connid=CONN_ID,
                    msg_total=1024,
                    recv_total=0,
                    outb=b"",
                ) 
                    for key, mask in events2:
                        c1_s2.service_connection(key, mask, data2)
                        #s2_sel.modify(key.fileobj, selectors.EVENT_READ | selectors.EVENT_WRITE , data=None)
                        s2_sel.modify(key.fileobj, selectors.EVENT_WRITE , data=None)
                        events2 = s2_sel.select(timeout=1)

            if primary_status == "S3" and c1_GFD.s3:
                # events3 = s3_sel.select(timeout=1)
                if c1_GFD.flag3 == 1:
                    print("Flag 3 GFD!!!!!!!!!!!!!!")
                    s3_sel.close()
                    s3_sel = selectors.DefaultSelector()
                    c1_s3 = Client(host2,port3,s3_sel, "S3")
                    c1_s3.start_connections()
                    c1_GFD.flag3 = None
                events3 = s3_sel.select(timeout=1)
                # print('Events3', events3)
                if events3[0][-1] != 1:  # writing data - mask != 1
                    # messages = messages + header_data + ";"
                    # messages = [bytes(messages, 'utf-8')]
                    data3 = types.SimpleNamespace(
                        connid=CONN_ID,
                        msg_total=1024,
                        recv_total=0,
                        messages=list(messages),
                        outb=b"",
                    )
                    for key, mask in events3:
                        c1_s3.service_connection(key, mask, data3)
                        s3_sel.modify(key.fileobj, selectors.EVENT_READ, data=None)
                        events2 = s3_sel.select(timeout=1)
                else:
                    data3 = types.SimpleNamespace(
                    connid=CONN_ID,
                    msg_total=1024,
                    recv_total=0,
                    outb=b"",
                ) 
                    for key, mask in events3:
                        c1_s3.service_connection(key, mask, data3)
                        #s3_sel.modify(key.fileobj, selectors.EVENT_READ | selectors.EVENT_WRITE , data=None)
                        s3_sel.modify(key.fileobj, selectors.EVENT_WRITE , data=None)
                        events3 = s3_sel.select(timeout=1)
        c1_s1.output = ""
        c1_s2.output = ""
        c1_s3.output = ""
    
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    s1_sel.close()
    s2_sel.close()
    s3_sel.close()