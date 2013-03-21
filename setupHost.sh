#!/bin/sh
echo Set IP address of eth0
ifconfig eth0 172.16.50.82
echo Set Standard Gateway
route add default gw 172.16.50.2

