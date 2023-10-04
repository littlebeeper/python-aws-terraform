import logging
from typing import Optional

from backend.db.model import Account
from backend.db.mongo_db_session import DbSessionMaker
from backend.db.mongo_setup import get_db, get_mongo_client

from backend.alerting import pager_duty_alert_on_exception

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def recalc(event, context):
    account_id: str = event.get('account_id')
    project_id: Optional[str] = event.get('project_id', None)
    debug: bool = event.get('debug')

    # account_id, start_date, random_seed, jira_instance: JIRA, github_instance: Github, jira_group_func, jql_addon=None, debug=False, run_id=None
    with DbSessionMaker(get_db(), get_mongo_client()) as dbs:
        account: Account = dbs.accounts_db.load_one(obj_id=account_id)
        logger.info(f"processing account: {account}")

    # log completion
    logger.info("recalculation complete!")


def handler(event, context):
    # print inputs
    logger.info(f"event: {event}")
    logger.info(f"context: {context}")

    # configs (from event)
    # - jira_server = 'https://issues.redhat.com' (if not present use account_id to resolve jira
    # - user_id = <propel user id>
    # - account_id = 'acct_123'
    # - project_ids = ['proj_123', 'proj_456']
    # - start_date = '2023-05-06'
    # - random_seed = 0
    # -
    # - debug = False

    try:
        recalc(event, context)
    except Exception as e:
        logger.error(f"Failed to recalc with ", exc_info=True)
        pager_duty_alert_on_exception(e, "recalc")
