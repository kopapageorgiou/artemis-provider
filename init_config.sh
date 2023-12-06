#! /bin/bash

# Then eth0 is the name of the interface that is connected to the private network
# change this to the name of your interface
# This is to get the internal ip
priv=`ip -4 addr show enp1s0 | grep inet | awk '{print $2}' | cut -d '/' -f1`

# To get the external ip
#priv=`wget -qO- ipinfo.io/ip`

echo PRIVATE_PEER_IP_ADDR=$priv > ./configuration/config.env
chmod +x ./configuration/config.env
