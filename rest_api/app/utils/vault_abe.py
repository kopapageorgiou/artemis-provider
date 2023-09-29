import json, requests, logging
from urllib3.exceptions import InsecureRequestWarning


LOGIN_ENDPOINT = "/v1/auth/userpass/login/"
ENCRYPTION_ENDPOINT = "/v1/abe/encrypt"
DECRYPTION_ENDPOINT = "/v1/abe/decrypt/"
class Vault():

    def __init__(self, host: str, username = "itrack_admin", password = "password") -> None:
        self._vault_host = host
        self._username = username
        response = requests.post(self._vault_host+LOGIN_ENDPOINT+self._username, json= {'password': password}, verify=False).json()
        
        self._client_token = response['auth']['client_token']
        self._headers = {'Content-Type': 'application/json',
                        'X-Vault-Token': self._client_token}
        logging.debug(self._headers)
        logging.debug("Successful vault login")
        
    def encrypt_abe(self, data: str, policy_attrs: list[str]) -> str:
        temp = []
        for attr in policy_attrs:
            temp.append(attr.replace("user", "userattr"))
        logging.debug("Key to encrypt:"+ data)
        try:
            logging.debug("1")
            policy = " or ".join(temp)
            logging.debug(f"2 with policy: {policy}")
            data_raw = {
                'message': data,
                'policy': policy
            }
            response = requests.post(self._vault_host+ENCRYPTION_ENDPOINT, headers=self._headers, json=data_raw, verify=False, timeout=600).json()
            logging.debug(response)
            if 'data' in response:
                logging.debug("4")
                return response['data']['b64_enc_data']
            else:
                logging.debug("5")
                return response['errors'][0]
        except Exception as e:
            logging.error(e)
            return "" 
        
    def decrypt_abe(self, encrypted_data: str, sub_policy: list[str]) -> str:
        try:
            policy = ' or '.join(sub_policy)
            data_raw = {
                "cryptogram": encrypted_data,
                "sub_policy": policy
            }
            response = requests.post(self._vault_host+DECRYPTION_ENDPOINT+self._username, headers=self._headers, json=data_raw, verify=False, timeout=600).json()
            if 'data' in response:
                return response['data']['decrypted_data']
            else:
                return response['errors'][0]
        except Exception as e:
            logging.error(e)
            return ""