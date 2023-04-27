#!/bin/sh
set -ex
ipfs bootstrap rm all
ipfs bootstrap add "/ip4/$(ip addr show | grep 'inet .* eth0' | awk '{print $2}' | cut -f1 -d'/')/tcp/4001/ipfs/$(ipfs config show | grep "PeerID" | awk -F '"' '{print $4}')"