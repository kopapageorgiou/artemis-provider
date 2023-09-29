#!/bin/sh
set -ex
ipfs bootstrap rm all

# Add bootstrap node for private network with internal ip
ipfs bootstrap add "/ip4/$(ip addr show | grep 'inet .* eth0' | awk '{print $2}' | cut -f1 -d'/')/tcp/4001/ipfs/$(ipfs config show | grep "PeerID" | awk -F '"' '{print $4}')"

#Add bootstrap node for private network with external ip
#ipfs bootstrap add "/ip4/$(wget -qO- ipinfo.io/ip)/tcp/4001/ipfs/$(ipfs config show | grep "PeerID" | awk -F '"' '{print $4}')"

FILE=/config.env
if grep -q "PRIVATE_PEER_ID=" "$FILE"; then
    cp $FILE /tmp/$FILE
    sed -i "s/^PRIVATE_PEER_ID=.*/PRIVATE_PEER_ID=$(ipfs config show | grep "PeerID" | awk -F '"' '{print $4}')/" /tmp/$FILE
    cat /tmp/$FILE > $FILE
    rm /tmp/$FILE
else
    echo "PRIVATE_PEER_ID=$(ipfs config show | grep "PeerID" | awk -F '"' '{print $4}')" >> $FILE
fi