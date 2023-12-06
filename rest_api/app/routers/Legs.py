import os, base64
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import logging
from Crypto.Random import get_random_bytes
from utils.vault_abe import Vault

router = APIRouter()
#abe_api = ABEAPI(f"http://{os.environ['ABE_HOST']}:12345")
logging.basicConfig(level=logging.DEBUG)

class Leg(BaseModel):
    device_id: int
    leg: list[str]

@router.post('/insertStations')
def insert_leg(leg: Leg, request: Request):
    try:
        vault: Vault = request.app.state.vault
        request.app.state.gate_stops[leg.device_id] = leg.leg
        request.app.state.gate_keys[leg.device_id] = base64.b64encode(get_random_bytes(32)).decode('utf-8')
        request.app.state.encrypted_symmetric_keys[leg.device_id] = vault.encrypt_abe(request.app.state.gate_keys[leg.device_id], policy_attrs= request.app.state.gate_stops[leg.device_id])
        return {"info": "Leg has been imported successfully", "code": 1}
    except Exception as e:
        logging.debug(e)
        raise HTTPException(status_code=500, detail=str(e))