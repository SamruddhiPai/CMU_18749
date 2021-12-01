#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import time, errno
from util import log
from threading import Thread
import config

server_active = 3

global membership_view 
membership_view = set()

class GFD_client(Thread):
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
        global membership_view
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
                send_message = "Sending " + str(repr(data.outb)) + " to RM"
                log(send_message)
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]
    def run(self):
        #server_found = str(input("Server on. LFD on? : "))
        global membership_view
        server_found = 'y'
        if (server_found == 'y' or server_found == 'Y'):
            self.start_connections(self.host, int(self.port))
            try:
                while True:
                    messages = 'GFD says I am alive;RM: '+str(len(membership_view))+ ' members: ' +  str(membership_view)
                    server_active = 3
                    
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


sel = selectors.DefaultSelector()

# LFD AS SERVER
class GFD_server(Thread):
    def __init__(self,host,port,sel):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.sel = sel
        self.membership = set()
    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        #events = selectors.EVENT_READ
        self.sel.register(conn, events, data=data)
        print("Accept Wrapper")

    def service_connection(self, key, mask):
        global membership_view
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            try:
                recv_data = sock.recv(1024)  # Should be ready to read
            except:
                recv_data = None
            recv_data_str = str(recv_data)
            datalist = recv_data_str.split(";")
            print("Shaktiman:", recv_data)
            
            if recv_data:
                print(recv_data)
                if recv_data == b'Send me the Status':
                    s = "+"
                    if "S1" in self.membership:
                        s += "S1"
                    if "S2" in self.membership:
                        s += "S2"
                    if "S3" in self.membership:
                        s += "S3"
                    data.outb = bytes(s, 'utf-8')
                print(data.outb)
                recv_data_str = str(recv_data)
                datalist = recv_data_str.split(";")
                add_members = recv_data_str
                if "S1" in add_members and "add" in add_members:
                    self.membership.add("S1")
                    data.outb = b"Add S1"
                elif "S1" in add_members and "delete" in add_members:
                    self.membership.discard("S1")
                    data.outb = b"Remove S1"
                if "S2" in add_members and "add" in add_members:
                    self.membership.add("S2")
                    data.outb = b"Add S2"
                elif "S2" in add_members and "delete" in add_members:
                    self.membership.discard("S2")
                    data.outb = b"Remove S2"
                if "S3" in add_members and "add" in add_members:
                    self.membership.add("S3")
                    data.outb = b"Add S3"
                elif "S3" in add_members and "delete" in add_members:
                    self.membership.discard("S3")
                    data.outb = b"Remove S3"
                if len(self.membership) == 0:
                    update = "GFD: 0 members"
                else:
                    update = "GFD: " + str(len(self.membership)) + " members:" + str(self.membership)
                log(update)
                
                membership_view = self.membership
                print("---------------------------------")
                    # data.outb = b'Acknowledgement'
                    #print('Updated data.outb')
                        
                    # except:
                    #     if (str(recv_data_str) == "b'Are you alive?'"):
                    #         data.outb = b'I am alive!'
            else:
                log(("Closing connection to " + str(data.addr)))
                self.sel.unregister(sock)
                sock.close()
                print("listening on", (host, port))
                
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:] #to clear data.outb
    
    def run(self):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((self.host, self.port))
        lsock.listen()
        print("\nListening on", (self.host, self.port))
        print("GFD: 0 members")
        lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)
        try:
            while True:
                # print(heart_beat)
                # time.sleep(heart_beat)
                events = self.sel.select(timeout=None) # Blocks until client ready for I/O, in effect till client sends data
                for key, mask in events:
                    if key.data is None: # key.data opaque class, will be assigned to ceratin type by client(ex: types.SimpleNamespace)
                        self.accept_wrapper(key.fileobj)
                    else:
                        self.service_connection(key, mask)
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        #finally:
            #self.sel.close()

#GFD As Server
sel_server = selectors.DefaultSelector()
host, port, num_conns = config.gfd_ip, config.gfd_listen, 1
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
gfd_server = GFD_server(host, port, sel_server)
gfd_server.start()


    

server_found = False

heart_beat = float(input('\nEnter heart beat frequency (in seconds): '))

#LFD AS SERVER
# CONN_ID = 10
# sel_server = selectors.DefaultSelector()
# # host_s, port_s, num_conns = '127.0.0.1', 1235, 1
# host_s, port_s, num_conns = config.gfd_ip, config.gfd_listen, 1
# gfd_server = GFD_server(host_s, port_s, sel_server)
# gfd_server.start()

# GFD AS CLIENT
#heart_beat = 1
CONN_ID = 10
sel_client = selectors.DefaultSelector()
host_c, port_c, num_conns = config.gfd_ip, config.rm_listen, 1

gfd_client = GFD_client(host_c, port_c, sel_client)
gfd_client.start()

