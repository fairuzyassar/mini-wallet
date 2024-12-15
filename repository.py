from sqlalchemy.orm import Session
from sqlalchemy import update, insert, select, desc
from models import Wallet, WalletState, WalletStatusType;

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
            
            stmt = (
                  update(Wallet)
                  .where(Wallet.wallet_id == wallet_id)
                  .values(status=status)
            )
            db.execute(statement=stmt)

            stmt = (
                 insert(WalletState).values(wallet_id=wallet_id, status=status)
            )
            db.execute(stmt)
            db.commit()
        except Exception as e:
            print(e)
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
         query = select(Wallet.balance).where(Wallet.customer_xid == customer_id)
         balance = db.execute(query).scalar()
         return balance