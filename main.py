from fastapi import FastAPI, Form, Depends, HTTPException, Request
from auhorization import JWT, HTTPAuthorization
from model.initRequest import InitRequest;
from typing import Annotated

app = FastAPI()
auth_validation = HTTPAuthorization()
# @app.exception_handler(HTTPException)
# async def custom_http_exception_handler(request: Request, exc: HTTPException):
#     print(exc)
#     return exc.detail

@app.post('/api/v1/init')
async def initWallet(data: Annotated[InitRequest, Form()]):
    print(data)
    try:
        token: str = JWT.generate_access_token(data.customer_xid, 15)
        return {
            "status": "success",
            "data" : {
                "token": token
            }
        }
    except Exception as e:
        print(e)
        return {
            "status": "failed",
            "data": None
        }
    
@app.post('/api/v1/wallet')
async def enableWallet(customer_idx: str = Depends(auth_validation)):
    return customer_idx
