from fastapi import FastAPI, Form, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from auhorization import JWT, HTTPAuthorization
from model.request import *;
from typing import Annotated
from sqlalchemy.orm import Session;
from database.database import get_db;
from models import Wallet, WalletState, WalletStatusType;
from repository import WalletRepo;
from model.response import *
app = FastAPI()
auth_validation = HTTPAuthorization()

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc: HTTPException):
    error_data = Response[ErrorResponseData](status=Status.FAILED, data=ErrorResponseData(error=exc.detail))
    return JSONResponse(status_code=exc.status_code, content=error_data.model_dump())


@app.post('/api/v1/init')
async def initWallet(data: Annotated[InitRequest, Form()], db: Session = Depends(get_db) ):
    try:
        user = WalletRepo.get_wallet_by_customer_idx(db, data.customer_xid)
        if user is None:
            WalletRepo.insert_new_wallet(db, data.customer_xid)
        token: str = JWT.generate_access_token(data.customer_xid, 15)
        return Response[TokenResponse](status=Status.SUCCESS, data=TokenResponse(token=token))
    except Exception as e:
        return Response[ErrorResponseData](status=Status.FAILED, data=ErrorResponseData(error="Failed to init account"))
    
@app.post('/api/v1/wallet')
async def enableWallet(customer_idx: str = Depends(auth_validation), db: Session = Depends(get_db)):
    status = WalletRepo.get_wallet_status_by_customer_xid(db, customer_idx)
    if status == WalletStatusType.ENABLE:
        return Response[ErrorResponseData](status=Status.FAILED, data=ErrorResponseData(error="wallet already enable"))
    WalletRepo.update_wallet_state(db, customer_idx, WalletStatusType.ENABLE)
    wallet, last_change_state_timestamp = WalletRepo.get_wallet_and_last_change_status_by_customer_xid(db, customer_idx)
    return Response[WalletStatusResponse](status=Status.SUCCESS, data=WalletStatusResponse(id=wallet.wallet_id, status=wallet.status, owned_by=wallet.customer_xid, balance=wallet.balance, change_at=last_change_state_timestamp))

@app.get('/api/v1/wallet')
async def getWalletBalance(customer_idx: str = Depends(auth_validation), db: Session = Depends(get_db)):
    balance = WalletRepo.get_wallet_balance_by_customer_xid(db, customer_idx)
    return balance

@app.patch('/api/v1/wallet')
async def disableWallet(data: Annotated[DisableRequest, Form()], customer_idx: str = Depends(auth_validation), db: Session = Depends(get_db)):
    if not data.is_disabled:
        return Response[ErrorResponseData](status=Status.FAILED, data=ErrorResponseData(error="Invalid value"))
    
    status = WalletRepo.get_wallet_status_by_customer_xid(db, customer_idx)
    if status == WalletStatusType.DISABLE:
        return Response[ErrorResponseData](status=Status.FAILED, data=ErrorResponseData(error="wallet already disable"))
    WalletRepo.update_wallet_state(db, customer_idx, WalletStatusType.DISABLE)
    wallet, last_change_state_timestamp = WalletRepo.get_wallet_and_last_change_status_by_customer_xid(db, customer_idx)
    return Response[WalletStatusResponse](status=Status.SUCCESS, data=WalletStatusResponse(id=wallet.wallet_id, status=wallet.status, owned_by=wallet.customer_xid, balance=wallet.balance, change_at=last_change_state_timestamp))
