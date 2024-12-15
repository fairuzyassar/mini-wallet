from pydantic import BaseModel

class InitRequest(BaseModel):
    customer_xid: str

class DisableRequest(BaseModel):
    is_disabled: bool

