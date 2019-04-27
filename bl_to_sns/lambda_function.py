import logging
import boto3
import traceback
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)
    try:
        sns = boto3.client('sns')
        topic_name = 'Backlog'
        snsTopicArn = [t['TopicArn'] for t in sns.list_topics()['Topics'] if t['TopicArn'].endswith(':' + topic_name)][0]

        sns.publish(
            TopicArn=snsTopicArn,
            Message=json.dumps(event),
            Subject='backlog'
        )

    except:
        logger.error(traceback.format_exc())
