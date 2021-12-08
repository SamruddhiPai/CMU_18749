localhost = "127.0.0.1"


############################################
#RM
rm_ip = localhost #"10.0.0.123"
rm_listen = 1290
############################################

#GFD
gfd_ip = localhost #"192.168.0.127"
gfd_listen = 1285

############################################

#server 1
server_1_ip = localhost #"192.168.0.127"
server_1_listen = 1200
server_1_sendto = 4000

server_1_listen_s2 = 1300
server_1_listen_s3 = 1301

#LFD 1
lfd_1_ip = localhost #"192.168.0.127"
lfd_1_listen = server_1_sendto
lfd_1_sendto = gfd_listen

############################################

#server 2
server_2_ip = localhost #"192.168.0.127"
server_2_listen = 1201
server_2_sendto = 4001

server_2_listen_s1 = 1302
server_2_listen_s3 = 1303

#LFD 2
lfd_2_ip = localhost #"192.168.0.127"
lfd_2_listen = server_2_sendto
lfd_2_sendto = gfd_listen

############################################

#server 3
server_3_ip = localhost #"192.168.0.127"
server_3_listen = 1202
server_3_sendto = 4002

server_3_listen_s2 = 1304
server_3_listen_s1 = 1305


#LFD 3
lfd_3_ip = localhost #"192.168.0.127"
lfd_3_listen = server_3_sendto
lfd_3_sendto = gfd_listen

#############################################



