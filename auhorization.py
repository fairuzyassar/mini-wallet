from jose import JWTError, jwt

from config import SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta
from fastapi.security import HTTPBasic, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException


class JWT():
    def generate_access_token(customer_id: str, expire_duration: int):
        expire_time = datetime.now() + timedelta(minutes=expire_duration)
        data = {
            "customer_id": customer_id,
            "expire_time": expire_time.isoformat(timespec='milliseconds')
        }

        encode_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        return encode_token
    
    def decode_access_token(encode_token: str):
        try:
            decode_token = jwt.decode(encode_token, SECRET_KEY, algorithms=[ALGORITHM])
            return decode_token
        except:
            return None


class HTTPAuthorization():
    async def __call__(self, request: Request):
        authorization = request.headers.get("Authorization")
        scheme, _, param = authorization.partition(" ")
        print(param)
        if not (authorization and scheme and param):
          raise HTTPException(
                    status_code=403, detail="Not Authorize Request"
                )
        if scheme.lower() != "token":
           raise HTTPException(
                    status_code=403,
                    detail="Token format not valid",
                )
        
        payload = JWT.decode_access_token(param)
        if not self.verify_token(payload):
            raise HTTPException(
                    status_code=403,
                    detail="Token Expire",
                )    
        return payload["customer_id"]
        
    def verify_token(self, payload: dict):
        if not payload:
            return False
        return payload["expire_time"] > datetime.now().isoformat(timespec='milliseconds')


        
