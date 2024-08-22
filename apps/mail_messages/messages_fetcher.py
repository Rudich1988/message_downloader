import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime as parse_datetime
from asgiref.sync import sync_to_async

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
        self.user_account = await (sync_to_async(UserEmailAccount.objects.get)
                                   (id=self.user_account_id))
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

    async def fetch_messages(self, flag):
        await self.load_account()
        await sync_to_async(self.connect)()
        messages = await sync_to_async(self._fetch)(flag=flag)
        await sync_to_async(self.disconnect)()
        return messages

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
