from fastapi import FastAPI
from cassandra.cluster import Cluster

cluster = Cluster(['172.20.0.3'])

app = FastAPI()

@app.post('/hello')
def hello():
    try:
        session = cluster.connect('mkeyspace')
        query= '''SELECT * FROM monkeySpecies'''
        rows = session.execute(query=query)
        return{"progress": [row for row in rows]}
    except Exception as e:
        return {"exception": e}