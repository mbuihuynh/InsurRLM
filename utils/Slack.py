import os
import logging
import requests
from datetime import datetime

import pathlib

logger = logging.getLogger()
logger.setLevel(logging.INFO)

webhook_url     = os.getenv('SLACK_WEBHOOK_URL')
webhook_channel = os.getenv('SLACK_WEBHOOK_CHANNEL')

proxies  = {
    'http': os.getenv('PROXY'),
    'https': os.getenv('PROXY')
}

class SlackWebhookBot:
    def __init__(self, timeout: int = 15):
        """Class to send messages to a provided Slack webhook URL.

        You can read more about Slack's Incoming Webhooks here:
            https://api.slack.com/messaging/webhooks

        Args:
            webhook_url: The webhook URL to send a message to.  Typically
                formatted like "https://hooks.slack.com/services/...".

        Kwargs:
            timeout: Number of seconds before the request will timeout.
                This is used to prevent a hang and is set to a default
                value of 15 seconds.
        """
        self.webhook_url = webhook_url
        self.timeout = timeout
        self.headers = {
            'Content-Type': 'application/json'
        }

    def send(self, message: str) -> bool:
        """Sends a message to the webhook URL.

        Per the Slack Incoming Webhook example.  The body of the request
        (for plain text) should be formatted as follows:
            `{"text": "Hello, World!"}`

        Args:
            message: Plain text string to send to Slack.

        Returns:
            A boolean representing if the request was successful.
        """
        success = False
        payload = {
            'text': message,
            'channel': webhook_channel
        }
        try:
            r = requests.post(
                self.webhook_url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout,
                proxies=proxies
            )
        except requests.Timeout:
            logger.error('Timeout occurred when trying to send message to Slack.')
        except requests.RequestException as e:
            logger.error(f'Error occurred when communicating with Slack: {e}.')
        else:
            success = True
            logger.info('Successfully sent message to Slack.')

        return success

    def generated_message(self, job_name, exp, msg_type):
        if msg_type == 'failed':
            msg = """
                :no_entry: _*Oop! Have a job failed!*_
                *:slack: Job name*: {}
                *:slack: Time*: {}
                *:slack: Error detail*: `{}`
            """.format(job_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), exp)
        else:
            msg = """
                :green_circle: _*Job run successfully!*_
                *:slack: Job name*: {}
                *:slack: Time*: {}
            """.format(job_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return msg

    def alert_job_failed(self, job_name, error_detail):
        msg = self.generated_message(job_name, error_detail, 'failed')
        return self.send(msg)

    def alert_job_success(self, job_name, error_detail):
        msg = self.generated_message(job_name, error_detail, 'success')
        return self.send(msg)

if __name__ == "__main__":
    path = str(pathlib.Path(__file__).absolute())
    oSlack = SlackWebhookBot()
    oSlack.alert_job_success(path, "test")