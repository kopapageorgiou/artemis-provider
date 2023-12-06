import os, logging
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from Orbitdbapi import OrbitdbAPI

router = APIRouter()
logging.basicConfig(level=logging.DEBUG)

class Query(BaseModel):
    database_name: str = Field(..., description="The name of the database to query")
    attribute: str = Field(..., description="The attribute to query")
    operator: str = Field(..., description="The operator to use in the query")
    value: str = Field(..., description="The value to query")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "database_name": "shared.measurements",
                    "attribute": "measurement_id",
                    "operator": "gt",
                    "value": "1"
                }
            ]
        }
    }


@router.post('/queryShared')
def query_shared_database(query: Query):
    try:
        orbitdb = OrbitdbAPI(orbithost=os.environ['ORBIT_HOST'], port=3000)
        db = orbitdb.load(dbname=query.database_name)
        result = db.query(query={
            "attribute": query.attribute,
            "operator": query.operator,
            "value": query.value
        })
        return {"info": "Query fetched successfully", "data": result['data']}
    except Exception as e:
        logging.debug(e)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/{database_name}')
def getAll(database_name: str):
    try:
        orbitdb = OrbitdbAPI(orbithost=os.environ['ORBIT_HOST'], port=3000)
        db = orbitdb.load(dbname=database_name)
        result = db.getAll()
        return {"info": "Query fetched successfully", "data": result['data']}
    except Exception as e:
        logging.debug(e)
        raise HTTPException(status_code=500, detail=str(e))