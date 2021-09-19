#!/usr/bin/env python3

import sys
import socket
import selectors
import types
<<<<<<< HEAD

sel = selectors.DefaultSelector()
#messages = [b"Message 1 from client.", b"Message 2 from client."]


def start_connections(host, port, messages):
    server_addr = (host, port)
    # for i in range(0, num_conns):
    connid = 1 #i + 1
    #print("starting connection", connid, "to", server_addr)
=======
import time, errno

heart_beat = int(input('Enter heart beat frequency (in seconds): '))
CONN_ID = 1
sel = selectors.DefaultSelector()

def start_connections(host, port):
    server_addr = (host, port)
    connid = 2
    print("starting connection", connid, "to", server_addr)
>>>>>>> main
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    # events = selectors.EVENT_WRITE
<<<<<<< HEAD
    data = types.SimpleNamespace(
        connid=connid,
        msg_total=1024,
        recv_total=0,
        messages=list(messages),
        outb=b"",
        # lfd=True
    )
    sel.register(sock, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
=======
    sel.register(sock, events, data=None)

def service_connection(key, mask, data):
    sock = key.fileobj
    #data = key.data
>>>>>>> main
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print("received", repr(recv_data), "from connection", data.connid)
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print("closing connection", data.connid)
            sel.unregister(sock)
            #sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
<<<<<<< HEAD
            print("sending", repr(data.outb), "to connection", data.connid)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


# from __future__ import division
# import sched
# import time

# scheduler = sched.scheduler(time.time, time.sleep)

# def schedule_it(frequency, duration, callable, *args):
#     no_of_events = int( duration / frequency )
#     priority = 1 # not used, lets you assign execution order to events scheduled for the same time
#     for i in range( no_of_events ):
#         delay = i * frequency
#         scheduler.enter( delay, priority, callable, args)

# def printer(x):
#     print x

# # execute printer 30 times a second for 60 seconds
# schedule_it(1/30, 60, printer, 'hello')
# scheduler.run()

#if len(sys.argv) != 4:
    #print("usage:", sys.argv[0], "<host> <port> <num_connections>")
    #sys.exit(1)
import time, errno
host, port, num_conns = '127.0.0.1', 1234, 1
heart_beat = int(input('Enter heart beat frequency'))
try:
    while True:
        # print("Enter a number:")
        messages = 'Are you alive?' #input()
        messages = [bytes(messages, 'utf-8')]
        start_connections(host, int(port), messages)
        events = sel.select(timeout=1)
        time.sleep(heart_beat)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        # Check for a socket being monitored to continue.
        #if not sel.get_map():
            #break
except IOError as e:
    if e.errno == errno.EPIPE:
        print('Server got disconnected')
        # pass
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
=======
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
    print('Server got disconnected')
        
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")

>>>>>>> main
# finally:
#     sel.close()