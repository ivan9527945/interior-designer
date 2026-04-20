from app.tasks.celery_app import celery_app


@celery_app.task(name="notifications.slack")
def send_slack_notification(channel: str, text: str) -> None:
    # TODO (Sprint 4): 接 Slack Incoming Webhook
    pass


@celery_app.task(name="notifications.email")
def send_email(to: str, subject: str, body: str) -> None:
    # TODO (Sprint 4): 接 SMTP / SES
    pass
