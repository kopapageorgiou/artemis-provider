from fastapi import FastAPI
from cassandra.cluster import Cluster
from requests import session
from routers import Clients, Gateways, Sensors, Measurements, GenerateKey, RetrieveData, Legs, Commit
import os, sys
import logging
from Orbitdbapi import OrbitdbAPI
from time import sleep
#import pip_system_certs.wrapt_requests
#import ipfshttpclient as ipfs
from utils.vault_abe import Vault
cluster = None

app = FastAPI()

def init():
    #app = FastAPI()
    app.state.gate_stops = {}
    app.state.gate_keys = {}
    app.state.gate_orders = {}
    app.state.encrypted_symmetric_keys = {}
    #app.state.gate_stops[14999] = ["user1", "user2", "user3", "user4", "user5"]
    #logging.debug(f"Init stations: {app.state.gate_stops[14999]}")
    #app.state.vault = Vault(f"https://{os.environ['VAULT_HOST']}:8200")
    try:
        app.state.vault = Vault("https://10.31.20.57:8200")
    except Exception as e:
        logging.error(f"could not connect to vault: {e}")
    app.include_router(Clients.router)
    app.include_router(Gateways.router)
    app.include_router(Sensors.router)
    app.include_router(Measurements.router)
    app.include_router(GenerateKey.router)
    app.include_router(RetrieveData.router)
    app.include_router(Legs.router)
    app.include_router(Commit.router)
    app.state.gate_keys = {}

while True:
    try:
        cluster = Cluster([os.environ['DB_HOST']])
        print("Got it")
        break
    except Exception:
        logging.warn('ScyllaDB server not available, retrying in 5 seconds...')
        sleep(5)
init()

# @app.post('/testOrbitdb')
# def hello():
#     try:
#         print(os.environ['ORBIT_HOST'], file=sys.stderr)
#         orbitdb = OrbitdbAPI(orbithost=os.environ['ORBIT_HOST'], port=3000)
#         db = orbitdb.load(dbname='test-base1')
#         print(db, file=sys.stderr)
#         res = db.insert(data={"key": 1, "name": "testName"})
#         print(res, file=sys.stderr)
#         res = db.query(query={"attribute": "name", "operator": "eq", "value": "testName"})
#         print(res, file=sys.stderr)
#         res = db.getAll()
#         print(res, file=sys.stderr)
#         #client = OrbitDbAPI(base_url=f"https://{os.environ['ORBIT_HOST']}:3000",timeout=60)
#         #print(res.json(), file=sys.stderr)
        
#         # with open('/etc/ssl/certs/X509Certificate.pem', 'rb') as infile:
#         #     customca = infile.read()
#         # with open(cafile, 'ab') as outfile:
#         #     outfile.write(b'\n')
#         #     outfile.write(customca)
#          #print(db, file=sys.stderr)
#         return{"Database": db}
#     except Exception as e:
#         print(e.args, file=sys.stderr)
#         return {"exception": e}