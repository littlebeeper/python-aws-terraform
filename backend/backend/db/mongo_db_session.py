from backend.db import AccountsDb
from backend.db.user_account_access_db import UserAccountAccessDb

from pymongo.client_session import ClientSession
from pymongo.database import Database
from pymongo.mongo_client import MongoClient


class DbSession:
    accounts_db: AccountsDb
    user_account_access_db: UserAccountAccessDb

    def __init__(self, db: Database, session: ClientSession):
        self.session = session
        self.accounts_db = AccountsDb(db=db, session=session)
        self.user_account_access_db = UserAccountAccessDb(db=db, session=session)

    def get_all_dbs(self):
        return [self.accounts_db, self.user_account_access_db]

    def close(self):
        self.session.end_session()

class CannotMakeMultipleSessions(Exception):
    pass


class ExitingSessionWhenNoSessionWasCreated(Exception):
    pass


class DbSessionMaker:
    def __init__(self, db: Database, mongo_client: MongoClient):
        self.db = db
        self.mongo_client = mongo_client
        self.session_created = False

    def __enter__(self):
        if self.session_created:
            raise CannotMakeMultipleSessions

        # options we could expose to opener of context:
        # - causal_consistency: Optional[bool] = None,
        # - default_transaction_options: Optional[client_session.TransactionOptions] = None,
        # - snapshot: Optional[bool] = False,

        self.current_session = DbSession(
            db=self.db,
            session=self.mongo_client.start_session())
                # causal_consistency=True))
        self.session_created = True
        return self.current_session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.session_created:
            raise ExitingSessionWhenNoSessionWasCreated
        self.current_session.close()
