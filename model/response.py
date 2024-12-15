from enum import Enum
from pydantic import BaseModel
from typing import Generic, TypeVar, Union
from datetime import datetime;

class Status(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"

class ErrorResponseData(BaseModel):
    error: str


T = TypeVar('T', bound=BaseModel)
class Response(BaseModel, Generic[T]):
    data:  Union[ErrorResponseData, T]
    status: Status

class TokenResponse(BaseModel):
    token: str

class BalanceResponse(BaseModel):
    balance: int 

class WalletStatusResponse(BaseModel):
    id: str
    owned_by: str
    status: str
    change_at: datetime
    balance: float 

