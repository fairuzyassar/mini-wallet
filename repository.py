from sqlalchemy.orm import Session
from sqlalchemy import update, insert, select, desc
from fastapi import HTTPException
from models import *;
from decimal import Decimal

class WalletRepo():
    @staticmethod
    def get_wallet_by_customer_idx(db: Session, customeridx: str):
        return db.query(Wallet).filter_by(customer_xid = customeridx).first()
    
    @staticmethod
    def insert_new_wallet(db: Session, customeridx: str):
            wallet = Wallet(customer_xid=customeridx, status=WalletStatusType.DISABLE)
            db.add(wallet)
            db.commit()
            db.refresh(wallet)

            wallet_state = WalletState(wallet_id=wallet.wallet_id, status=WalletStatusType.DISABLE)
            db.add(wallet_state)
            db.commit()
            db.refresh(wallet_state)

    def update_wallet_state(db: Session, customeridx: str, status: WalletStatusType):
        try:
            wallet_id_query = select(Wallet.wallet_id).where(Wallet.customer_xid == customeridx)
            wallet_id = db.execute(wallet_id_query).scalar()
            
            query = (
                  update(Wallet)
                  .where(Wallet.wallet_id == wallet_id)
                  .values(status=status)
            )
            db.execute(statement=query)

            query = (
                 insert(WalletState).values(wallet_id=wallet_id, status=status)
            )
            db.execute(statement=query)
            db.commit()
        except Exception as e:
            db.rollback() 

    def get_wallet_status_by_customer_xid(db: Session, customer_id: str):
         query = select(Wallet.status).where(Wallet.customer_xid == customer_id)
         status = db.execute(query).scalar()
         return status
    
    def get_wallet_and_last_change_status_by_customer_xid(db: Session, customer_id: str):
         query = (select(Wallet, WalletState.changed_at)
                  .join(WalletState, Wallet.wallet_id == WalletState.wallet_id).where(Wallet.customer_xid == customer_id)
                  .order_by(desc(WalletState.changed_at)))
         result = db.execute(query).first()
         wallet, last_change_state_timestamp = result
         return wallet, last_change_state_timestamp
    
    def get_wallet_balance_by_customer_xid(db: Session, customer_id: str):
         query = select(Wallet.balance, Wallet.status).where(Wallet.customer_xid == customer_id)
         balance, status = db.execute(query).scalar()
         if status == WalletStatusType.DISABLE:
            raise HTTPException(status_code=400, detail="Wallet Disable")

         return balance
    
class TransactionRepo():
     def create_transaction(db: Session, reference_id: str, customer_id: str, amount: float, type: TransactionType):
         try:
            query = select(Wallet.wallet_id, Wallet.status).where(Wallet.customer_xid == customer_id)
            wallet_id, wallet_status = db.execute(query).first()
            if wallet_status == WalletStatusType.DISABLE:
                raise HTTPException(status_code=400, detail="Wallet Disable")
            
            query = select(Transaction).where(Transaction.reference_id == reference_id)
            result = db.execute(query).first()
            if result:
                raise HTTPException(status_code=400, detail="Reference id is exist")
            
            transaction = Transaction(
                reference_id=reference_id, 
                wallet_id=wallet_id, 
                amount=amount, 
                status=TransactionStatusType.CREATED, 
                type=type
            )
            db.add(transaction)

            transaction_state = TransactionState(status=TransactionStatusType.CREATED, reference_id=reference_id)
            db.add(transaction_state)
            db.commit()
         except Exception as e:
             db.rollback()
             raise HTTPException(500, detail=str(e))

     
     def process_transaction(db: Session, reference_id: str, customer_id: str, amount: float, type: TransactionType):
        try:
            query = select(Wallet).where(Wallet.customer_xid == customer_id).with_for_update()
            wallet = db.execute(query).scalar_one_or_none()
            if wallet is None:
                raise HTTPException(status_code=404, detail="Wallet not found for the given customer ID")

            transaction = db.execute(select(Transaction).where(Transaction.reference_id == reference_id)).scalar_one_or_none()
            if not transaction:
                raise HTTPException(status_code=404, detail="Transaction not found")

            db.execute(update(Transaction).where(Transaction.reference_id == reference_id).values(status=TransactionStatusType.PROCESSING))

            transaction_state = TransactionState(status=TransactionStatusType.PROCESSING, reference_id=reference_id)
            db.add(transaction_state)

            if type == TransactionType.WITHDRAWN and wallet.balance < Decimal(amount):
                db.execute(update(Transaction).where(Transaction.reference_id == reference_id).values(status=TransactionStatusType.FAILED))
                db.add(TransactionState(status=TransactionStatusType.FAILED, reference_id=reference_id))
                db.commit()
                raise HTTPException(status_code=400, detail="Insufficient balance")

            new_balance = (Decimal(wallet.balance) + Decimal(amount) 
                        if type == TransactionType.DEPOSIT 
                        else Decimal(wallet.balance) - Decimal(amount))
            db.execute(update(Wallet).where(Wallet.wallet_id == wallet.wallet_id).values(balance=new_balance))

            db.execute(update(Transaction).where(Transaction.reference_id == reference_id).values(status=TransactionStatusType.SUCCESS))
            db.add(TransactionState(status=TransactionStatusType.SUCCESS, reference_id=reference_id))

            db.commit()

            return True
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        
     def get_transaction_and_state_by_reference_id(db: Session, reference_id: str):
         result = db.execute(select(Transaction, TransactionState.changed_at)
                                  .join(TransactionState, Transaction.reference_id == TransactionState.reference_id)
                                  .where(Transaction.reference_id == reference_id).order_by(desc(TransactionState.changed_at))).first()
         transaction, timestamp = result
         return transaction, timestamp
\
               
          
          
            

