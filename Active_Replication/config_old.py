#GFD
gfd_ip = "10.0.0.166"
gfd_listen = 1285

############################################

#server 1
server_1_ip = "10.0.0.183"
server_1_listen = 1200
server_1_sendto = 4000
#LFD 1
lfd_1_ip = "10.0.0.183"
lfd_1_listen = server_1_sendto
lfd_1_sendto = gfd_listen

############################################

#server 2
server_2_ip = "127.0.0.1"
server_2_listen = 1201
server_2_sendto = 4001
#LFD 2
lfd_2_ip = "127.0.0.1"
lfd_2_listen = server_2_sendto
lfd_2_sendto = gfd_listen

############################################

#server 3
server_3_ip = "127.0.0.1"
server_3_listen = 1202
server_3_sendto = 4002
#LFD 3
lfd_3_ip = "127.0.0.1"
lfd_3_listen = server_3_sendto
lfd_3_sendto = gfd_listen


#############################################

