import os, sys, logging, base64
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from utils.vault_abe import Vault
router = APIRouter()
logging.basicConfig(level=logging.DEBUG)

class Gateway(BaseModel):
    gateway_id: int
    poi_id: str

logging.basicConfig(level=logging.DEBUG)
@router.post('/generateKey')
def generate_key(gateway: Gateway, request: Request):
    try:
        vault: Vault = request.app.state.vault
        request.app.state.gate_stops[gateway.gateway_id].remove(gateway.poi_id)
        #logging.debug("Stations: "+str(request.app.state.gate_stops[gateway.gateway_id]))
        request.app.state.gate_keys[gateway.gateway_id] = base64.b64encode(get_random_bytes(32)).decode('utf-8')
        #request.app.state.encrypted_symmetric_keys[gateway.gateway_id] = request.app.state.gate_keys[gateway.gateway_id]
        request.app.state.encrypted_symmetric_keys[gateway.gateway_id] = vault.encrypt_abe(request.app.state.gate_keys[gateway.gateway_id],
                                                                                    policy_attrs= request.app.state.gate_stops[gateway.gateway_id])
        logging.debug(request.app.state.gate_keys)
        return {"info": "Key changed", "code": 1}
    except Exception as e:
        logging.debug(e)
        raise  HTTPException(status_code=500, detail=str(e))