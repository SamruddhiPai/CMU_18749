#!/usr/bin/env python3

import sys
import socket
import selectors
import types

CONN_ID = 1
sel = selectors.DefaultSelector()

def start_connections(host, port):
    server_addr = (host, port)
<<<<<<< HEAD
    for i in range(0, num_conns):
        connid = i + 1
        #print("starting connection", connid, "to", server_addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        #events = selectors.EVENT_READ | selectors.EVENT_WRITE
        events = selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            connid=connid,
            msg_total=1024,
            recv_total=0,
            messages=list(messages),
            outb=b"",
            # lfd=False
        )
        sel.register(sock, events, data=data)

=======
    connid = 2
    print("starting connection", connid, "to", server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)
    #events = selectors.EVENT_READ | selectors.EVENT_WRITE
    events = selectors.EVENT_WRITE
    sel.register(sock, events, data=None)
>>>>>>> main

def service_connection(key, mask, data):
    sock = key.fileobj
    #data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print("received", repr(recv_data), "from connection", data.connid)
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            #print("closing connection", data.connid)
            sel.unregister(sock)
            #sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            #print("sending", repr(data.outb), "to connection", data.connid)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

<<<<<<< HEAD

#if len(sys.argv) != 4:
    #print("usage:", sys.argv[0], "<host> <port> <num_connections>")
    #sys.exit(1)

host, port, num_conns = '127.0.0.1', 1234, 1 
=======
host, port, num_conns = '127.0.0.1', 1234, 1
start_connections(host, int(port))
>>>>>>> main

try:
    while True:
        print("Enter a number:")
        messages = input()
        messages = [bytes(messages, 'utf-8')]
        data = types.SimpleNamespace(
            connid=CONN_ID,
            msg_total=1024,
            recv_total=0,
            messages=list(messages),
            outb=b"",
        )
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask, data)
        # Check for a socket being monitored to continue.
        #if not sel.get_map():
            #break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()