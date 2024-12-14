from pydantic import BaseModel

class InitRequest(BaseModel):
    customer_xid: str