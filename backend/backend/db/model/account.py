from typing import ClassVar, Optional
from backend.db.model.model import Model


class Account(Model):
    token_prefix: ClassVar[str] = 'acct'
    __collection__ = 'accounts'

    name: str

    gates: dict[str, bool] = {}

    def has_gate(self, name):
        return self.gates.get(name, False)
