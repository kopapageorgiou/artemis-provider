from fastapi import FastAPI
from cassandra.cluster import Cluster
from routers import Clients, Gateways, Sensors, Measurements
from orbitdbapi import OrbitDbAPI
import os, sys
import logging
#import pip_system_certs.wrapt_requests
#import ipfshttpclient as ipfs
import requests
import certifi
import orbitdbapi

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
        print(os.environ['ORBIT_HOST'], file=sys.stderr)
        #ipfs_client = ipfs.connect('/dns/172.21.0.2/tcp/5001/http')
        BASE = f"http://{os.environ['ORBIT_HOST']}:3000"
        #client = OrbitDbAPI(base_url=f"https://{os.environ['ORBIT_HOST']}:3000",timeout=60)
        res = requests.post(BASE+'/insertData', json={"name": "test-base1", "type": "docstore", "data": {"_id": 1, "name": "testName"}})
        #print(res.json(), file=sys.stderr)
        
        # with open('/etc/ssl/certs/X509Certificate.pem', 'rb') as infile:
        #     customca = infile.read()
        # with open(cafile, 'ab') as outfile:
        #     outfile.write(b'\n')
        #     outfile.write(customca)
         #print(db, file=sys.stderr)
        return{"Databases": res.json()}
    except Exception as e:
        print(e.args, file=sys.stderr)
        return {"exception": e}