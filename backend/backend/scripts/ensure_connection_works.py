from backend.db.mongo_setup import get_mongo_client
from backend.env import Environment
from backend.scripts.helpers import setup_env

setup_env(Environment.QA)
client = get_mongo_client()
print(client.list_databases())
