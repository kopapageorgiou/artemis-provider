import os, sys, logging, base64
from fastapi import APIRouter, Request
from pydantic import BaseModel
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

router = APIRouter()
logging.basicConfig(level=logging.DEBUG)

class Gateway(BaseModel):
    gateway_id: int


@router.post('/generateKey')
def generate_key(gateway: Gateway, request: Request):
    try:
        request.app.state.gate_keys[gateway.gateway_id] = base64.b64encode(get_random_bytes(32)).decode('utf-8')
        logging.debug(request.app.state.gate_keys)
        return {"info": "Key changed", "code": 1}
    except Exception as e:
        logging.debug(e)
        return {"info": e, "code": 0}