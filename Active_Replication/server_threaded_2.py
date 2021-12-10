#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import time
from util import log
from threading import Thread
import config


CHECK_POINT_FREQ = 5
CHECK_POIN_NUM = 0
glob_mem = ''
prev_mem = ''

class Server_as_Server(Thread):
    def __init__(self, host, port, sel):
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

    # X = 0

    def service_connection(self, key, mask):
        global X
        sock = key.fileobj
        data = key.data
        original_X = X
        if mask & selectors.EVENT_READ:
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
                    X += int(num)
                    update = "X = " + str(original_X) + " ---> " + "X = " + str(X)
                    log(update)
                    print("------")
                    data.outb = b'Acknowledgement'
                    print('Updated data.outb')
                    
                except:
                    if (str(recv_data_str) == "b'Are you alive?'"):
                        data.outb = b'I am alive!'
            else:
                log(("Closing connection to " + str(data.addr)))
                self.sel.unregister(sock)
                sock.close()
                print("listening on", (self.host, self.port))
                    
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:] #to clear data.outb
        
    def run(self):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((self.host, self.port))
        lsock.listen()
        print("listening on", (self.host, self.port))
        lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)

        print("X = " + str(X))
        print("------")

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




class Server_as_Client(Thread):
    def __init__(self, host, port, sel):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.sel = sel

    def start_connections(self,host, port):
        server_addr = (host, port)
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
                # log(receive_str)
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
                # log(send_message)
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

    def run(self):
        self.start_connections(self.host, int(self.port))
        try:
            while True:
                messages = 'I am a server and I am up.'
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

        except IOError as e:
            close_message = "Server got disconnected"
            log(close_message)
                
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")

class Server_as_Client_to_Primary(Thread):
    def __init__(self, host, port, sel):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.sel = sel

    def start_connections(self,host, port):
        server_addr = (host, port)
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
            print(str(recv_data))
            if recv_data:
                recv_data_str = recv_data.decode("utf-8")
                print(recv_data_str)
                datalist = recv_data_str.split(';')
                log('Current State: '+ str(datalist[0]))
                log('Checkpoint Value: ' + str(datalist[1]))
                receive_str = "Received status (X) from from Primary Server as " + datalist[0] + " and check point number is "+ datalist[1]
                log(receive_str)
                X = int(datalist[0])
                checkpoint_counter = int(datalist[1])
                # checkpoint_msg = "Checkpoint counter on server 2 is updated to " + str(checkpoint_counter)
                # print('-----Received X-----')
                # log(str(X))
                # print('-----Received checkpoint is------')
                # log(str(checkpoint_msg))

                data.recv_total += len(recv_data)
            if not recv_data or data.recv_total == data.msg_total:
                close_message = "Closing Connection " + str(data.connid)
                log(close_message)
                self.sel.unregister(sock)

    def run(self):
        self.start_connections(self.host, int(self.port))
        try:
            while True:
                data = types.SimpleNamespace(
                    connid=CONN_ID,
                    msg_total=1024,
                    recv_total=0,
                    outb=b"",
                )
                events = self.sel.select(timeout=1)
                if events:
                    for key, mask in events:
                        self.service_connection(key, mask, data)

        except IOError as e:
            close_message = "Server got disconnected"
            log(close_message)
                
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")


class Server_as_Primary_Replica(Thread):
    
    def __init__(self, host , port1, port2, sel1, sel2):
        Thread.__init__(self)
        self.host = host
        self.port1 = port1
        self.sel1 = sel1
        self.port2 = port2
        self.sel2 = sel2

    def accept_wrapper(self, sock, sel):
        conn, addr = sock.accept()  # Should be ready to read
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        sel.register(conn, events, data=data)

    def service_connection(self, key, mask, sel):
        global X
        global CHECK_POIN_NUM
        sock = key.fileobj
        data = key.data
                    
        if mask & selectors.EVENT_WRITE:
            state = X
            checkpoint_msg = str(state) + ';' + str(CHECK_POIN_NUM)
            data.outb = bytes(checkpoint_msg, 'utf-8')
            try:
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:] #to clear data.outb
            except:
                log(("Closing connection to " + str(data.addr)))
                sel.unregister(sock)
                sock.close()

        
    def run(self):
        global CHECK_POIN_NUM
        global glob_mem
        global prev_mem
        
        lsock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock1.bind((self.host, self.port1))
        lsock1.listen()
        print("listening on", (self.host, self.port1))
        lsock1.setblocking(False)
        self.sel1.register(lsock1, selectors.EVENT_WRITE | selectors.EVENT_READ , data=None)

        lsock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock2.bind((self.host, self.port2))
        lsock2.listen()
        print("listening on", (self.host, self.port2))
        lsock2.setblocking(False)
        self.sel2.register(lsock2, selectors.EVENT_WRITE | selectors.EVENT_READ, data=None)

        try:
            while True:
                events1 = self.sel1.select(timeout=0.5) # Blocks until client ready for I/O, in effect till client sends data
                if glob_mem != prev_mem:
                    if ('S1' in glob_mem and 'S1' not in prev_mem):
                        
                        for key, mask in events1:
                            if key.data is None: # key.data opaque class, will be assigned to ceratin type by client(ex: types.SimpleNamespace)
                                self.accept_wrapper(key.fileobj, self.sel1)
                            else:
                                self.service_connection(key, mask, self.sel1)
                                print("Checkpoint Sent to Backup Replica Server 1")
                                CHECK_POIN_NUM += 1
                                time.sleep(CHECK_POINT_FREQ)
                                prev_mem = glob_mem
                    if ('S1' not in glob_mem and 'S1' in prev_mem):
                        self.sel1.unregister(key.fileobj)
                        key.fileobj.close()
                        prev_mem = glob_mem

                events2 = self.sel2.select(timeout=0.5) # Blocks until client ready for I/O, in effect till client sends data
                if glob_mem != prev_mem:
                    if ('S3' in glob_mem and 'S3' not in prev_mem):
                        for key, mask in events2:
                            if key.data is None: # key.data opaque class, will be assigned to ceratin type by client(ex: types.SimpleNamespace)
                                self.accept_wrapper(key.fileobj, self.sel2)
                            else:
                                self.service_connection(key, mask, self.sel2)
                                print("Checkpoint Sent to Backup Replica Server 2")
                                CHECK_POIN_NUM += 1
                                time.sleep(CHECK_POINT_FREQ)
                                prev_mem = glob_mem
                    if ('S3' not in glob_mem and 'S3' in prev_mem):
                        self.sel2.unregister(key.fileobj)
                        key.fileobj.close()
                        prev_mem = glob_mem

        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.sel1.close()
            self.sel2.close()

connid = 1

#host_s, port_s = '127.0.0.1', 1234
host_s, port_s = config.server_2_ip, config.server_2_listen
sel_server = selectors.DefaultSelector()
X = 0
server_as_server = Server_as_Server(host_s, port_s, sel_server)
server_as_server.start()


CONN_ID = 10
# host_c, port_c = '127.0.0.1', 1235
host_c, port_c = config.server_2_ip, config.server_2_sendto
sel_client = selectors.DefaultSelector()
server_as_client = Server_as_Client(host_c, port_c, sel_client)
server_as_client.start()

# Receive Checkpoint from S1

CONN_ID_p = 11
host_p, port_p = config.server_1_ip, config.server_1_listen_s2
sel_client_to_p = selectors.DefaultSelector()
server_as_client_to_p = Server_as_Client_to_Primary(host_p, port_p, sel_client_to_p)
server_as_client_to_p.start()

# Receive Checkpoint from S3

CONN_ID_p = 11
host_p, port_p = config.server_3_ip, config.server_3_listen_s2
sel_client_to_p = selectors.DefaultSelector()
server_as_client_to_p = Server_as_Client_to_Primary(host_p, port_p, sel_client_to_p)
server_as_client_to_p.start()
# Establishing Connection to replica S1 and S3


host_s, port_s1, port_s3 = config.server_2_ip, config.server_2_listen_s1, config.server_2_listen_s3
sel_server1 = selectors.DefaultSelector()
sel_server3 = selectors.DefaultSelector()

server_as_primary_replica1 = Server_as_Primary_Replica(host_s, port_s1, port_s3, sel_server1, sel_server3)
server_as_primary_replica1.start()