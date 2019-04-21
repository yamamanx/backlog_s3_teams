import logging
import boto3
import json
import traceback
import os
from teams import Teams

logger = logging.getLogger()
logger.setLevel(logging.INFO)


changes_field = {
    'summary': '件名',
    'description': '詳細',
    'milestone': 'マイルストーン',
    'startDate': '開始日',
    'limitDate': '期限日',
    'estimatedHours': '予定時間',
    'actualHours': '実績時間',
    'assigner': '担当者',
    'status': '状態'
}


status = {
    '1': '未対応',
    '2': '処理中',
    '3': '処理済み',
    '4': '完了'
}


def get_changes(changes):
    if len(changes) == 0:
        return ''

    changes_str = '<b>変更内容:</b><br>'
    for change in changes:
        field = change.get('field', '')
        old = change.get('old_value', '')
        new = change.get('new_value', '')

        if field == 'status':
            old = status.get(old, '')
            new = status.get(new, '')

        changes_str += '{field}: {old} => {new}<br>'.format(
            field=changes_field.get(field, '不明フィールド'),
            old=old,
            new=new
        )

    return changes_str


def get_comment(comment):
    if len(comment) == 0:
        return ''

    return '<b>コメント:</b> {comment}<br>'.format(
        comment=comment
    )


def get_value(message, key):
    if key in message:
        if message[key]:
            return message[key]

    if key == 'actualHours' or key == 'estimatedHours':
        return 0

    return ''


def lambda_handler(event, context):
    teams = Teams()
    try:
        domain = os.environ.get('BACKLOG_DOMAIN', '')

        for record in event['Records']:
            message_body = json.loads(record['body'])
            message = json.loads(message_body['Message'])

            logger.info(message)

            project = get_value(message, 'project')
            content = get_value(message, 'content')
            createdUser = get_value(message, 'createdUser')

            project_name = get_value(project, 'name')
            projectKey = get_value(project, 'projectKey')
            key_id = get_value(content, 'key_id')
            summary = get_value(content, 'summary')
            milestone_array = get_value(content, 'milestone')
            if len(milestone_array) > 0:
                milestone = get_value(milestone_array[0], 'name')
            else:
                milestone = ''
            estimatedHours = round(get_value(content, 'estimatedHours'), 2)
            actualHours = round(get_value(content, 'actualHours'), 2)
            comment = get_value(get_value(content, 'comment'), 'content')
            status = get_value(get_value(content, 'status'), 'name')
            user = get_value(createdUser, 'name')
            assignee = get_value(get_value(content, 'assignee'), 'name')

            changes = get_value(content, 'changes')

            url = 'https://{domain}/view/{projectKey}-{key_id}'.format(
                domain=domain,
                projectKey=projectKey,
                key_id=key_id
            )
            url_tag = '<a href="{url}">{url}</a>'.format(
                url=url
            )

            response = teams.send_message(
                '{summary} ({milestone})'.format(
                    summary=summary,
                    milestone=milestone
                ),
                '<b>対応状況:</b> {status}<br><b>担当:</b> {assignee}<br><b>実績時間:</b> {actualHours}<br><b>予定時間:</b> {estimatedHours}<br>{url}<br><b>更新者:</b> {user}<br>{comment}{changes}'.format(
                    status=status,
                    user=user,
                    comment=get_comment(comment),
                    actualHours=actualHours,
                    estimatedHours=estimatedHours,
                    url=url_tag,
                    assignee=assignee,
                    changes=get_changes(changes)
                )
            )

            logger.info(response)
            logger.info(response.text)

    except:
        logger.error(traceback.format_exc())
        raise Exception(traceback.format_exc())