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
    if key == 'estimatedHours' or key == 'actualHours':
        return 0
    if key == 'startDate' or key == 'dueDate':
        return '9999-12-31'
    return ''


def lambda_handler(event, context):
    teams = Teams()
    try:
        s3 = boto3.resource('s3')
        bucket_name = os.environ.get('BUCKET_NAME', None)

        for record in event['Records']:
            message_body = json.loads(record['body'])
            message = json.loads(message_body['Message'])

            project = get_value(message, 'project')
            content = get_value(message, 'content')

            projectKey = get_value(project, 'projectKey')
            key_id = get_value(content, 'key_id')

            object_key = '{projectKey}-{key_id}.json'.format(
                projectKey=projectKey,
                key_id=key_id
            )

            obj = s3.Object(
                bucket_name,
                object_key
            )

            milestone_array = get_value(content, 'milestone')
            if len(milestone_array) > 0:
                milestone = get_value(milestone_array[0], 'name')
            else:
                milestone = ''
            estimatedHours = get_value(content, 'estimatedHours')
            actualHours = get_value(content, 'actualHours')
            status = get_value(get_value(content, 'status'), 'name')
            assignee = get_value(get_value(content, 'assignee'), 'name')
            issueType = get_value(get_value(content, 'issueType'), 'name')
            startDate = get_value(content, 'startDate')
            dueDate = get_value(content, 'dueDate')
            summary = get_value(content, 'summary')

            ticket_json = {
                'milestone': milestone,
                'estimatedHours': estimatedHours,
                'actualHours': actualHours,
                'status': status,
                'assignee': assignee,
                'issueType': issueType,
                'startDate': startDate,
                'dueDate': dueDate,
                'summary': summary
            }

            response = obj.put(
                Body=json.dumps(ticket_json)
            )

            logger.info(response)

    except:
        logger.error(traceback.format_exc())
        teams.send_message(
            'Error',
            traceback.format_exc()
        )
        raise Exception(traceback.format_exc())
