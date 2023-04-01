from fastapi import FastAPI
from cassandra.cluster import Cluster
from routers import Clients, Gateways, Sensors, Measurements
from orbitdbapi import OrbitDbAPI
import os, sys
import logging
#import ipfshttpclient as ipfs
import requests

cluster = Cluster([os.environ['DB_HOST']])

app = FastAPI()

app.include_router(Clients.router)
app.include_router(Gateways.router)
app.include_router(Sensors.router)
app.include_router(Measurements.router)

@app.post('/test')
def hello():
    try:
        session = cluster.connect('mkeyspace')
        query= '''SELECT * FROM clients'''
        rows = session.execute(query=query)
        return{"values from clients table": [row for row in rows]}
    except Exception as e:
        return {"exception": e}
    
@app.post('/testOrbitdb')
def hello():
    try:
        #ipfs_client = ipfs.connect('/dns/172.21.0.2/tcp/5001/http')
        client = OrbitDbAPI(base_url=f"http://{os.environ['ORBIT_HOST']}:3000", timeout=600)
        print(os.environ['ORBIT_HOST'], file=sys.stderr)
        db = client.db('my-feed')
        print("here2", file=sys.stderr)
        return{"Databases": client.list_dbs()}
    except Exception as e:
        print(e.args, file=sys.stderr)
        return {"exception": e}