from backend.db.model import Account
from backend.db.mongo_db_session import DbSession

def is_gate_enabled(db: DbSession, account_id, gate_name):
    account: Account = db.accounts_db.load_one(account_id)
    return account.gates.get(gate_name, False)
