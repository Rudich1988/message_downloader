import json
from random import randint
from time import sleep
from django.shortcuts import redirect
from django.views import View
from django.http import HttpResponseBadRequest
#from django.utils.dateparse import parse_datetime
from email.utils import parsedate_to_datetime as parse_datetime
import imaplib
from email import message_from_bytes
from channels.generic.websocket import AsyncWebsocketConsumer
from email.header import decode_header

from .models import EmailMessage
from apps.accounts.models import UserEmailAccount


class EmailConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        pass
        #await self.accept()






class EmailFetcher:
    def __init__(self, email, password, imap_server, user_account_id):
        self.email = email
        self.password = password
        self.imap_server = imap_server
        self.mail = None
        self.user_account = UserEmailAccount.objects.get(id=user_account_id)

    def connect(self):
        self.mail = imaplib.IMAP4_SSL(self.imap_server)
        self.mail.login(self.email, self.password)

    def disconnect(self):
        if self.mail:
            self.mail.logout()
            self.mail = None

    def fetch_emails(self, folder='inbox'):
        if not self.mail:
            raise Exception("Not connected to any email server. Call connect() first.")

        self.mail.select(folder)
        result, data = self.mail.search(None, 'ALL')
        email_ids = data[0].split()
        for eid in email_ids:
            result, msg_data = self.mail.fetch(eid, '(RFC822)')
            msg = message_from_bytes(msg_data[0][1])
            self.save_message(msg)

    def save_message(self, msg):
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else 'utf-8')

        sent_date = msg.get('Date')
        if sent_date:
            sent_date = parse_datetime(sent_date)

        # Get email body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition'))
                if 'attachment' not in content_disposition:
                    payload = part.get_payload(decode=True)
                    if payload:
                        try:
                            body = payload.decode()
                        except UnicodeDecodeError:
                            # Handle cases where decoding fails
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
        EmailMessage.objects.create(
            account=self.user_account,
            title=subject,
            sent_date=sent_date,
            received_date=parse_datetime(msg.get('Date')),  # Assuming received date is the same as sent date
            body=body,
            attachments=attachments
        )


class SaveEmail(View):
    def get(self, request, account_id):
        #try:
        email_account = UserEmailAccount.objects.get(id=account_id)
        email_fetcher = EmailFetcher(
            email=email_account.email,
            password=email_account.password,
            imap_server='imap.' + email_account.email.split('@')[1],
            user_account_id=account_id
        )
        email_fetcher.connect()
        email_fetcher.fetch_emails()
        email_fetcher.disconnect()
        return redirect('index')

        #except Exception:
         #   return HttpResponseBadRequest("User account not found.")
