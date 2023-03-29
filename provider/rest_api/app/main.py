from fastapi import FastAPI
from cassandra.cluster import Cluster
import os

cluster = Cluster([os.environ['DB_HOST']])

app = FastAPI()

@app.post('/hello')
def hello():
    try:
        session = cluster.connect('mkeyspace')
        query= '''SELECT * FROM sensors'''
        rows = session.execute(query=query)
        return{"progress": [row for row in rows]}
    except Exception as e:
        return {"exception": e}