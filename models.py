from sqlalchemy import Column, DECIMAL, String, func, ForeignKey, TIMESTAMP, Enum as SqlEnum
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum
import uuid
from database.database import Base

metadata = Base.metadata

class WalletStatusType(str, Enum):
    ENABLE = "Enable"
    DISABLE = "Disable"

class TransactionType(str, Enum):
    DEPOSIT = "Deposit"
    WITHDRAWN = "WithDrawn"

class TransactionStatusType(str, Enum):
    CREATED = "Created"
    PROCESSING = "Processing"
    SUCCESS = "Success"
    FAILED = "Failed"

class Wallet(Base):  
    __tablename__ = "wallet"
    wallet_id  = Column(String(36), primary_key=True, default=lambda : str(uuid.uuid4()))
    customer_xid = Column(String(36), nullable=False, index=True)
    balance = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    status = Column(SqlEnum(WalletStatusType), nullable=False)

class WalletState(Base):
    __tablename__ = "wallet_state"
    id = Column(String(36), primary_key=True, default=lambda : str(uuid.uuid4()))
    wallet_id = Column(String(36), ForeignKey("wallet.wallet_id"), nullable=False, index=True)
    status = Column(SqlEnum(WalletStatusType), nullable=False)
    changed_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

class Transaction(Base):
    __tablename__ = "transaction"
    reference_id = Column(String(100), primary_key=True)
    wallet_id = Column(String(36), ForeignKey("wallet.wallet_id"), nullable=False, index=True)
    status = Column(SqlEnum(TransactionStatusType), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    type = Column(SqlEnum(TransactionType), nullable=False)

class TransactionState(Base):
    __tablename__ = "transaction_state"
    id = Column(String(36), primary_key=True, default=lambda : str(uuid.uuid4()))
    reference_id = Column(String(36), ForeignKey("transaction.reference_id"), nullable=False, index=True)
    status = Column(SqlEnum(TransactionStatusType), nullable=False)
    changed_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

