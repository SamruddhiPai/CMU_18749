# Counting likes on a distributed social media network

Distributed client server application for manipulating a global variable that keeps the count of
likes on a post for any social media profile.
In this project, TCP communication is established in between three clients and a server. 
There are 2 server replicas for building a reliable distributed system that can simulatenously handle 2 faults.
Each server has its local fault detector and the system is managed by a global fault detector and replication manager
is responsible for concensus and membership.
Active as well as Passive replication is implemented.
