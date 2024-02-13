from math import log
import os, sys, logging, base64
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from utils.vault_abe import Vault
from cassandra.cluster import Cluster
from cassandra.query import dict_factory
from datetime import datetime
router = APIRouter()
logging.basicConfig(level=logging.DEBUG)
sys.tracebacklimit = 0
class Commit(BaseModel):
    hash_string: str
    signature: str
    gateway_id: str
    begin_t: str
    end_t: str

class Range(BaseModel):
    gateway_id: str
    begin_t: str
    end_t: str

cluster = Cluster([os.environ['DB_HOST']])
logging.basicConfig(level=logging.DEBUG)
@router.post('/commit')
def generate_key(commit: Commit, request: Request):
    try:
        session = cluster.connect('mkeyspace')
        query = '''INSERT INTO commitments
        (hash_string, signature, gateway_id, begin_t, end_t)
        VALUES (%s, %s, %s, %s, %s)'''
        values = (commit.hash_string,
                    commit.signature,
                    commit.gateway_id,
                    commit.begin_t,
                    commit.end_t, )
        session.execute(query=query, parameters=values)
        session.shutdown()
        return {"info": "Commitment stored", "code": 1}
    except Exception as e:
        logging.debug(e)
        raise  HTTPException(status_code=500, detail=str(e))
    
@router.post('/retrieveRange')
def retrieve_range(rng: Range, request: Request):
    try:
        session = cluster.connect('mkeyspace')
        query = '''SELECT * FROM commitments
        WHERE gateway_id = %s ALLOW FILTERING'''
        values = (rng.gateway_id, )
        total_commitments = session.execute(query=query, parameters=values).all()
        total_commitments.sort(key=lambda x: x.begin_t)

        lowest = None
        highest = None
        commits = []
        guard = True
        for index, row in enumerate(total_commitments):
            start_t = row.begin_t
            end_t = row.end_t
            if lowest is None:
                logging.debug(f"{index} {start_t}")
                if index == 0 and datetime.strptime(rng.begin_t, '%Y-%m-%d %H:%M:%S') <= start_t:
                    lowest = start_t
                    guard = False
                elif start_t <= datetime.strptime(rng.begin_t, '%Y-%m-%d %H:%M:%S') <= end_t:
                    lowest = start_t
                    guard = False
            
            if lowest != None and highest == None:
                if start_t <= datetime.strptime(rng.end_t, '%Y-%m-%d %H:%M:%S') <= end_t:
                    highest = end_t
                    commits.append(row._asdict())
                    break
                elif index == len(total_commitments) - 1 and datetime.strptime(rng.end_t, '%Y-%m-%d %H:%M:%S') >= end_t:
                    highest = end_t
                    commits.append(row._asdict())
                    break
            if not guard:
                commits.append(row._asdict())
        #logging.debug(commits)
        # query = '''SELECT * FROM commitments
        # WHERE gateway_id = %s AND begin_t >= %s AND begin_t < %s ALLOW FILTERING'''
        # values = (rng.gateway_id, lowest, highest)
        # rows = session.execute(query=query, parameters=values).all()
        #logging.debug(rows)
        #logging.debug(lowest, highest)
        query = '''SELECT measurement_time, measurement_value FROM measurements
        WHERE sensor_id = %s AND measurement_time >= %s AND measurement_time <= %s'''
        values = ("14300store 1", lowest, highest, )
        #values = (rng.gateway_id, lowest, highest, )
        session.row_factory = dict_factory
        measurement_values = session.execute(query=query, parameters=values).all()
        for row in measurement_values:
            row['measurement_time'] = row['measurement_time'].strftime("%Y-%m-%d %H:%M:%S")
        temp = []
        session.shutdown()
        return {"info": "Commitment ranges", "code": 1, "ranges": commits, "measurements": measurement_values}
    except Exception as e:
        logging.debug(e)
        raise  HTTPException(status_code=500, detail=str(e))