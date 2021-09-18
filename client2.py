#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import time

CONN_ID = 2
sel = selectors.DefaultSelector()

host, port, num_conns = '127.0.0.1', 1234, 1

def log(stringarg):
    now = time.localtime()
    year = str(now.tm_year)
    month = str(now.tm_mon)
    day = str(now.tm_mday)
    hour = str(now.tm_hour)
    min = str(now.tm_min)
    sec = str(now.tm_sec)
    timeStr = year + "/" + month + "/" + day + "_" + hour + ":" + min + ":" + sec
    printstr = str(timeStr) + " : " + stringarg
    print(printstr)

def start_connections(host, port):
    server_addr = (host, port)
    connid = CONN_ID
    print("starting connection", connid, "to", server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    #events = selectors.EVENT_WRITE
    sel.register(sock, events, data=None)

def service_connection(key, mask, data):
    sock = key.fileobj
    #data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            receive_str = "Received " + str(repr(recv_data)) + " from connection " + str(data.connid)
            log(receive_str)
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
            req_str = "Sending " + str(repr(data.outb)) + " to Server " + str(host) + ":" + str(port)
            log(req_str)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

start_connections(host, int(port))
try:
    while True:
        print()
        log("Enter a number:")
        header_type = "REQ;"
        header_message = "from client: " + str(CONN_ID) + ";"
        messages = "" + header_type + header_message
        header_data = input()

        messages = messages + header_data + ";"
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