#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import time
from util import log

sel = selectors.DefaultSelector()

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    #events = selectors.EVENT_READ
    sel.register(conn, events, data=data)

membership = set()
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        recv_data_str = str(recv_data)
        datalist = recv_data_str.split(";")
        if recv_data:
            print(recv_data)
            if recv_data == b'Send me the Status':
                s = "+"
                if "S1" in membership:
                    s += "S1"
                if "S2" in membership:
                    s += "S2"
                if "S3" in membership:
                    s += "S3"
                data.outb = bytes(s, 'utf-8')
            print(data.outb)
            if len(datalist) > 2:
                recv_data_str = str(recv_data)
                datalist = recv_data_str.split(";")
                add_members = datalist[2]
                if "S1" in add_members and "add" in add_members:
                    membership.add("S1")
                    data.outb = b"Add S1"
                elif "S1" in add_members and "delete" in add_members:
                    membership.discard("S1")
                    data.outb = b"Remove S1"
                if "S2" in add_members and "add" in add_members:
                    membership.add("S2")
                    data.outb = b"Add S2"
                elif "S2" in add_members and "delete" in add_members:
                    membership.discard("S2")
                    data.outb = b"Remove S2"
                if "S3" in add_members and "add" in add_members:
                    membership.add("S3")
                    data.outb = b"Add S3"
                elif "S3" in add_members and "delete" in add_members:
                    membership.discard("S3")
                    data.outb = b"Remove S3"
                if len(membership) == 0:
                    update = "High Alert! All server replicas dead!"
                else:
                    update = "GFD: " + str(len(membership)) + " members:" + str(membership)
                log(update)
                print("---------------------------------")
                # data.outb = b'Acknowledgement'
                #print('Updated data.outb')
                    
                # except:
                #     if (str(recv_data_str) == "b'Are you alive?'"):
                #         data.outb = b'I am alive!'
        else:
            log(("Closing connection to " + str(data.addr)))
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:] #to clear data.outb

host, port = '127.0.0.1', 1285
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print("listening on", (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None) # Blocks until client ready for I/O, in effect till client sends data
        for key, mask in events:
            if key.data is None: # key.data opaque class, will be assigned to ceratin type by client(ex: types.SimpleNamespace)
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()