#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import time, errno

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

heart_beat = int(input('Enter heart beat frequency (in seconds): '))
CONN_ID = 1
sel = selectors.DefaultSelector()

def start_connections(host, port):
    server_addr = (host, port)
    connid = 2
    print("Starting connection", connid, "to", server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    # events = selectors.EVENT_WRITE
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
            close_message = "Closing Connection " + str(data.connid)
            log(close_message)
            sel.unregister(sock)
            #sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            #print("sending", repr(data.outb), "to connection", data.connid)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

host, port, num_conns = '127.0.0.1', 1234, 1
start_connections(host, int(port))

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
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask, data)
        # Check for a socket being monitored to continue.
        #if not sel.get_map():
            #break
        time.sleep(heart_beat)

except IOError as e:
    # if e.errno == errno.EPIPE:
    close_message = "Server got disconnected"
    log(close_message)
        
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")

# finally:
#     sel.close()