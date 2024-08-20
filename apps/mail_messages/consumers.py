import json
import imaplib
from time import sleep
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime as parse_datetime

import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async

from .models import EmailMessage
from apps.accounts.models import UserEmailAccount


class EmailFetcher:
    def __init__(self, user_account_id):
        self.user_account_id = user_account_id
        self.user_account = None
        self.email = None
        self.password = None
        self.imap_server = None
        self.mail = None

    async def load_account(self):
        self.user_account = await sync_to_async(UserEmailAccount.objects.get)(id=self.user_account_id)
        self.email = self.user_account.email
        self.password = self.user_account.password
        self.imap_server = 'imap.' + self.email.split('@')[1]

    def connect(self):
        self.mail = imaplib.IMAP4_SSL(self.imap_server)
        self.mail.login(self.email, self.password)

    def disconnect(self):
        if self.mail:
            self.mail.logout()
            self.mail = None

    async def fetch_messages(self):
        await self.load_account()
        await sync_to_async(self.connect)()
        #messages = await sync_to_async(self._fetch)('ALL')#(flag='RECENT')
        messages = await sync_to_async(EmailMessageConsumer()._fetch)(flag='ALL', fetcher=self, mail=self.mail)#(flag='RECENT')
        await sync_to_async(self.disconnect)()
        return messages

    '''
    def _fetch(self, flag):
        self.mail.select("inbox")
        status, messages = self.mail.search(None, flag)
        if status != "OK":
            return []
        messages = messages[0].split()
        result = []
        for msg_num in messages:
            status, msg_data = self.mail.fetch(msg_num, "(RFC822)")
            if status != "OK":
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            data = self.create_data_message(msg)
            result.append(data)
        return result
    '''

    def create_data_message(self, msg):
        if 'Subject' in msg:
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else 'utf-8')
        else:
            subject = ''
        sent_date = msg.get('Date')
        if sent_date:
            sent_date = parse_datetime(sent_date)
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get('Content-Disposition'))
                if 'attachment' not in content_disposition:
                    payload = part.get_payload(decode=True)
                    if payload:
                        try:
                            body = payload.decode()
                        except UnicodeDecodeError:
                            body = payload.decode(errors='replace')
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                try:
                    body = payload.decode()
                except UnicodeDecodeError:
                    body = payload.decode(errors='replace')
        attachments = []
        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get('Content-Disposition'))
                if 'attachment' in content_disposition:
                    filename = part.get_filename()
                    attachments.append(filename)
        message_data = {
            "title": subject,
            "sent_date": sent_date,
            "received_date": parse_datetime(msg.get('Date')),
            "body": body,
            "attachments": attachments,
        }
        return message_data



class EmailMessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.email_account_id = self.scope['url_route']['kwargs']['email_account_id']
        self.group_name = f"email_messages_{self.email_account_id}"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        await self.fetch_and_send_new_messages()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def fetch_and_send_new_messages(self):
        account = await sync_to_async(UserEmailAccount.objects.get)(id=self.email_account_id)
        fetcher = EmailFetcher(account.id)
        new_messages = await fetcher.fetch_messages()
        progress = 0
        for message_data in new_messages:
            progress += 1
            new_message = await sync_to_async(EmailMessage.objects.create)(
                account=account,
                title=message_data['title'],
                sent_date=message_data['sent_date'],
                received_date=message_data['received_date'],
                body=message_data['body'],
                attachments=message_data['attachments'],
            )
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'send_message',
                    'message': {
                        'id': new_message.id,
                        'title': new_message.title,
                        'body': new_message.body,
                        'received_date': new_message.received_date.isoformat(),
                        'sent_date': new_message.sent_date.isoformat(),
                        'progress': progress,
                    }
                }
            )
            await self.send(text_data=json.dumps({
                'type': 'progress_update',
                'progress': progress,
            }))
            await asyncio.sleep(1)

    async def send_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': message
        }))
        progress = message.get('progress', 0)
        if progress > 0:
            await self.send(text_data=json.dumps({
                'type': 'progress_update',
                'progress': progress
            }))
            await asyncio.sleep(1)
        await asyncio.sleep(1)

    def _fetch(self, mail, flag, fetcher):
        mail.select("inbox")
        status, messages = mail.search(None, flag)
        if status != "OK":
            return []
        messages = messages[0].split()
        result = []
        for msg_num in messages:
            status, msg_data = mail.fetch(msg_num, "(RFC822)")
            if status != "OK":
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            data = fetcher.create_data_message(msg)
            result.append(data)
        return result
