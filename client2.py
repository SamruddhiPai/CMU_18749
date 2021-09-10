#!/usr/bin/env python3

import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()

def start_connections(host, port, num_conns, messages):
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        print("starting connection to", server_addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            connid=connid,
            msg_total=1024,
            recv_total=0,
            messages=list(messages),
            outb=b"",
        )
        sel.register(sock, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            # print("received", repr(recv_data), "from connection", data.connid)
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print("closing connection", data.connid)
            sel.unregister(sock)
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


if len(sys.argv) != 1:
    print("usage:", sys.argv[0])
    sys.exit(1)

host = '127.0.0.1'
port = 1234
num_conns = 1

try:
    while True:
        print("Enter a number:")
        messages = input()
        messages = [bytes(messages, 'utf-8')]
        start_connections(host, int(port), 1, messages)
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()