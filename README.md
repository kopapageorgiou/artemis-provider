# Artemis Provider implementation
---
## Requirements
* Docker
* Docker-compose plug-in
* Python3
* Go-lang

## Initialization
1. To initialize configuration file for IPFS: <code>./init_config.sh</code>
2. To generate a swarm key: <code>go run generate_swarm.go > ./ipfs/swarm.key</code>
## Build
Run the command:
<code>docker-compose build</code>

## Start containers
Run the command:
<code>docker-compose up -d</code>
**NOTE:** To initialize ScyllaDB tables run:
1. <code>pip install scylla-driver</code>
2. <code>python initScyllaTables.py</code>

### Acknowledgement
The script used to generate swarm key can be found in: https://github.com/Kubuxu/go-ipfs-swarm-key-gen