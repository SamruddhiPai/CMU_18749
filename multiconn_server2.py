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

X = 0

def service_connection(key, mask):
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
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:] #to clear data.outb

host, port = '127.0.0.1', 1235
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print("listening on", (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

print("X = " + str(X))
print("------")

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