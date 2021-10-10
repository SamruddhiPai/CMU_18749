#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import time, errno
from util import log


heart_beat = 1 #float(input('Enter heart beat frequency (in seconds): '))
CONN_ID = 10
sel = selectors.DefaultSelector()
host, port, num_conns = '127.0.0.1', 1234, 1

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
            receive_str = "Received " + str(repr(recv_data)) + " from Server"+" "+ str(host) + ":" + str(port)
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
            if (not len(stack)) or (stack[-1] != 2):
                send_message = "Sending " + str(repr(data.outb)) + " to Server" +" "+ str(host) + ":" + str(port)
                log(send_message)
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]


start_connections(host, int(port))
server_connection_buffer = 1
macOS_buffer = 0
resistance = server_connection_buffer + macOS_buffer
stack = []
try:
    while True:
        if resistance == 0:
            if (len(stack) == 2):
                l1 = stack.pop()
                l2 = stack.pop()
                if not(l1 in [1,3] and l2 == 2):
                    dead = "Heartbeat Fail! Server is dead!"
                    log(dead)
                    break
        else:
            resistance -= 1
            if len(stack):
                stack.pop()
        messages = 'Are you alive?'
        messages = [bytes(messages, 'utf-8')]
        data = types.SimpleNamespace(
                    connid=CONN_ID,
                    msg_total=1024,
                    recv_total=0,
                    messages=list(messages),
                    outb=b"",
                )
        events = sel.select()#timeout=1)
        if events:
            for key, mask in events:
                flag = mask
                service_connection(key, mask, data)  
        stack.append(flag)
        time.sleep(heart_beat)
except IOError as e:
    close_message = "Server got disconnected"
    log(close_message)
        
except KeyboardInterrupt:
    log("caught keyboard interrupt, exiting")

