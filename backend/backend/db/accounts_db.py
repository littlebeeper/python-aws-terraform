from backend.db.mongo_db import MongoDb
from backend.db.model.account import Account

class AccountsDb(MongoDb):
    model = Account

    def load_all(self) -> list[Account]:
        return super().load_all()

    def count(self, filter_dict={}) -> int:
        return super().count(filter_dict)
