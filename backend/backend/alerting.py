import boto3
import json

import logging
from logging import getLogger

from backend.config import Config
from backend.config_deps import app_config

logger = getLogger()
logger.setLevel(logging.INFO)



def pager_duty_alert_on_exception(e: Exception, context: str):
    config: Config = app_config()

    if config.is_testing_or_development():
        logger.info(f"Skipping pagerduty alert in {config.env} environment")
        return

    try:
        sns_client = boto3.client('sns', region_name='us-west-1')

        message = {
            "NewStateValue": "ALARM",
            "context": context,
            "error": str(e),
            "env": config.env.value,
        }

        # Publish a ping message to the SNS topic
        response = sns_client.publish(
            TopicArn=config.pagerduty_sns_topic_arn,
            Message=json.dumps(message),
            Subject=f'ALARM: {context}',
        )
        logger.info(f"Successfully published to SNS topic {config.pagerduty_sns_topic_arn} with response {response}")
    except Exception as sns_topic_error:
        logger.error(f'Failed to publish to SNS topic: {config.pagerduty_sns_topic_arn}, error: {sns_topic_error}')
