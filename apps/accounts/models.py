import imaplib
import email
from email.header import decode_header

from email.utils import parsedate_to_datetime as parse_datetime
from django.db import models

from apps.users.models import CustomUser


class UserEmailAccount(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    '''
    def fetch_messages(self, flag='RECENT'):
        mail = imaplib.IMAP4_SSL(self.get_imap_server())
        mail.login(self.email, self.password)
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
            data = self.create_data_message(msg)
            result.append(data)
        return result

    def create_data_message(self, msg):
        if 'Subject' in msg:
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else 'utf-8')
        else:
            subject = None

        sent_date = msg.get('Date')
        if sent_date:
            sent_date = parse_datetime(sent_date)
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                # content_type = part.get_content_type()
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
        message_data = {
            "title": subject,
            "sent_date": sent_date,
            "received_date": parse_datetime(msg.get('Date')),
            "body": body,
            "attachments": attachments,
        }
        return message_data

    def get_imap_server(self):
        return 'imap.' + self.email.split('@')[1]
    '''





    '''
            msg_subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(msg_subject, bytes):
                msg_subject = msg_subject.decode(encoding if encoding else "utf-8")
            msg_date = email.utils.parsedate_to_datetime(msg.get("Date"))
            msg_body = ""

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        msg_body += part.get_payload(decode=True).decode(part.get_content_charset())
            else:
                msg_body = msg.get_payload(decode=True).decode(msg.get_content_charset())

            # Преобразуем данные в формат, пригодный для сохранения
            message_data = {
                "title": msg_subject,
                "sent_date": msg_date,
                "received_date": datetime.datetime.now(),
                "body": msg_body,
                "attachments": [],
            }

            result.append(message_data)

        mail.logout()
        return result

    def get_imap_server(self):
        if "gmail.com" in self.email:
            return "imap.gmail.com"
        elif "yandex.ru" in self.email:
            return "imap.yandex.ru"
        # Добавьте другие почтовые сервисы по необходимости
        return "default.imap.server"

    def __str__(self):
        return self.email
    '''