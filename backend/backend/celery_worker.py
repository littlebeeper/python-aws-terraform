from typing import Optional

from celery import Celery

from backend.config_deps import app_config

from backend.db.mongo_db_session import DbSessionMaker
from backend.db.mongo_setup import get_db, get_mongo_client

# Assumes CELERY_BROKER_URL is set in the environment
celery_app = Celery('tasks')

@celery_app.task
def create_project_epic_and_send_email_to_dri(account_id: str, project_id: str, jira_user_id: Optional[str] = None):
    print(f"Arguments are: {account_id}, {project_id}, {jira_user_id}")
    print("DB CONFIG IS: ", app_config().mongo_db_config)

    with DbSessionMaker(get_db(), get_mongo_client()) as dbs:
        pass

