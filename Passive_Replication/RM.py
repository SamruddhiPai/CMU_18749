#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import time
from util import log
import config
# import primary_status
# import GFD_threaded
import subprocess
# import passive_server_1
# import passive_server_2
# import passive_server_3


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


sel = selectors.DefaultSelector()

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    #events = selectors.EVENT_READ
    sel.register(conn, events, data=data)

membership = set()
# add_members = []
recv_data_str = ""
primary_replica = ""
s = ""
def service_connection(key, mask):
    global s
    global primary_replica 
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(1024)  # Should be ready to read
            # print("Debugging Shaktimaan:",recv_data)
        except:
            recv_data = None
        recv_data_str = str(recv_data)
        datalist = recv_data_str.split(";")
        if recv_data:
            # print(recv_data)
            if recv_data == b'Send me the Status':
                s = "+"
                if "S1" in recv_data_str:
                    print("OK")
                    s += "S1+"
                if "S2" in recv_data_str:
                    print("OK2")
                    s += "S2+"
                if "S3" in recv_data_str:
                    print("OK3")
                    s += "S3+"
                
            #print(data.outb)
            # print('s',s)
            memb_view_list = list(membership) #s.split('+')
            print(color.BOLD + color.PURPLE + 'Hello World !' + color.END)
            # print(color.BOLD + color.GREEN + "MEMB = " + color.END, memb_view_list)
            if (primary_replica == ""):
                if (len(memb_view_list) == 1):
                    primary_replica = memb_view_list[0]
                    data.outb = bytes('Primary Server is %s'%(primary_replica), 'utf-8')
                
            print("PRIMARY IS", primary_replica)
            
            f = open("out.txt", "w")
            f.write(primary_replica)
            f.close()
            
            if (primary_replica not in memb_view_list):
                print("TIME TO ELECT!!!")
                if (len(memb_view_list) > 0):
                    primary_replica = memb_view_list[0]
                    data.outb = bytes('Primary Server is %s'%(primary_replica), 'utf-8')
                    print("ELECTED", primary_replica)
                    # if (primary_status.primary_replica == "S1"):
                    #     passive_server_1.server_as_primary_replica1.start()
                    #     passive_server_2.server_as_client_to_p.start()
                    # elif (primary_status.primary_replica == "S2"):
                    #     passive_server_2.server_as_primary_replica2.start()
                    #     passive_server_1.server_as_client_to_p.start()
                    # elif (primary_status.primary_replica == "S3"):
                    #     passive_server_3.server_as_primary_replica1.start()
                else:
                    primary_replica = ""

            recv_data_str = str(recv_data)
            add_members = recv_data_str#.split(";")
            # add_members = recv_data_str
            # membership.add(add_members)
            # print('Add members',add_members)
            log(add_members)
            # add_members = add_members[1]
            # print(add_members[1].split('members:'))
            if "S1" in add_members:
                membership.add("S1")
            else:
                membership.discard("S1")
            # elif "S1" in add_members and "delete" in add_members:
            #     membership.discard("S1")
            #     data.outb = b"Remove S1"
            if "S2" in add_members:# and "add" in add_members:
                membership.add("S2")
            else:
                membership.discard("S2")
                # data.outb = b"Add S2"
            # elif "S2" in add_members and "delete" in add_members:
            #     membership.discard("S2")
            #     data.outb = b"Remove S2"
            if "S3" in add_members: # and "add" in add_members:
                membership.add("S3")
            else:
                membership.discard("S3")
                # data.outb = b"Add S3"
            # elif "S3" in add_members and "delete" in add_members:
            #     membership.discard("S3")
            #     data.outb = b"Remove S3"
            if len(membership) == 0:
                update = "RM: 0 members"
            else:
                update = "RM: " + str(len(membership)) + " members:" + str(membership)
            log(update)
            print("---------------------------------")
            #     # data.outb = b'Acknowledgement'
            #     #print('Updated data.outb')
                    
            #     # except:
            #     #     if (str(recv_data_str) == "b'Are you alive?'"):
            #     #         data.outb = b'I am alive!'
        else:
            log(("Closing connection to " + str(data.addr)))
            sel.unregister(sock)
            sock.close()
            print("listening on", (host, port))
            
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:] #to clear data.outb

host, port = config.rm_ip, config.rm_listen
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print("listening on", (host, port))
print("RM: 0 members")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    f = open("out.txt", "w")
    f.write("")
    f.close()

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
    print("Finally")
    sel.close()