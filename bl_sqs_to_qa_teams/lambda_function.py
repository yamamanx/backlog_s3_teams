import logging
import boto3
import json
import traceback
import os
from teams import Teams

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_value(message, key):
    logger.debug(message)
    logger.debug(key)
    if key in message:
        if message[key]:
            logger.debug(message[key])
            return message[key]
    return ''


def lambda_handler(event, context):
    teams = Teams()
    try:
        domain = os.environ.get('BACKLOG_DOMAIN', '')
        milestone = int(os.environ.get('QA_MILESTONE', '0'))

        for record in event['Records']:
            message_body = json.loads(record['body'])
            message = json.loads(message_body['Message'])

            project = get_value(message, 'project')
            content = get_value(message, 'content')
            createdUser = get_value(message, 'createdUser')

            milestone_array = get_value(content, 'milestone')
            if len(milestone_array) > 0:
                milestone_id = get_value(milestone_array[0], 'id')
            else:
                return

            if milestone_id != milestone:
                return

            projectKey = get_value(project, 'projectKey')
            key_id = get_value(content, 'key_id')

            description = get_value(content, 'description')

            comment = get_value(get_value(content, 'comment'), 'content')
            user = get_value(createdUser, 'name')

            url = 'https://{domain}/view/{projectKey}-{key_id}'.format(
                domain=domain,
                projectKey=projectKey,
                key_id=key_id
            )
            url_tag = '<a href="{url}">{url}</a>'.format(
                url=url
            )

            teams.send_message(
                '回答',
                '**質問**:{description}<br><br>**{user}の回答**:{comment}<br><br>{url}'.format(
                    description=description,
                    user=user,
                    comment=comment,
                    url=url_tag
                )
            )
    except:
        logger.error(traceback.format_exc())
        raise Exception(traceback.format_exc())