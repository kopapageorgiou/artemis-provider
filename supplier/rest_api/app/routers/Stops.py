import os
from fastapi import APIRouter
from pydantic import BaseModel
from cassandra.cluster import Cluster


cluster = Cluster([os.environ['DB_HOST']])
router = APIRouter()

class Stops(BaseModel):
    customer_id: str
    stop_id: str
    location: str

@router.post('/insertStops')
def insert_stops(stops: Stops):
    try:
        session = cluster.connect('mkeyspace')
        query = '''INSERT INTO stops (customer_id,stop_id,location) VALUES (%s,%s,%s)'''
        values = (stops.customer_id,
                stops.stop_id,
                stops.location)
        session.execute(query=query, parameters=values)
        session.shutdown()
        return {"info": "Stop has been imported successfully", "code": 1}
    except Exception as e:
        return {"info": e, "code": 0}