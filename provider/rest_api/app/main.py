from fastapi import FastAPI
from cassandra.cluster import Cluster
from routers import Clients, Gateways, Sensors, Measurements
import os

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