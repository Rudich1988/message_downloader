import json
from asgiref.sync import sync_to_async
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer

from .models import EmailMessage
from apps.accounts.models import UserEmailAccount
from .messages_fetcher import EmailFetcher


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
        account = await (sync_to_async(UserEmailAccount.objects.get)
                         (id=self.email_account_id))
        fetcher = EmailFetcher(account.id)
        has_messages = await sync_to_async(EmailMessage.objects.filter
                                           (account=account).exists)()
        flag = 'RECENT' if has_messages else 'ALL'
        new_messages = await fetcher.fetch_messages(flag=flag)
        regress = len(new_messages)
        progress = 0
        for message_data in new_messages:
            regress -= 1
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
                        'regress': regress,
                    }
                }
            )
            await self.send(text_data=json.dumps({
                'type': 'progress_update',
                'progress': progress,
            }))
            await asyncio.sleep(0.5)

    async def send_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': message
        }))
        regress = message.get('regress', 0)
        if regress >= 0:
            await self.send(text_data=json.dumps({
                'type': 'progress_update',
                'progress': regress
            }))
        await asyncio.sleep(0.5)
