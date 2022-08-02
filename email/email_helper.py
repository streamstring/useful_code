import logging
import smtplib
from email.message import EmailMessage
import mimetypes
from pathlib import PurePath


class EmailHelper:
    def __init__(self, subject, tto, ffrom, bcc=None
                 , filename='Email.xlsx'
                 , maintype='application'
                 , subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
        temp_msg = EmailMessage()
        temp_msg['Subject'] = subject
        temp_msg['To'] = tto
        temp_msg['From'] = ffrom
        if bcc:
            self._bcc = bcc
            temp_msg['Bcc'] = list(bcc)
        self._subject, self._to, self._from,  = subject, tto, ffrom
        self._filename, self._maintype, self._subtype = filename, maintype, subtype
        self._smtp_server, self._smtp_port = 'smtp.larksuite.com', 465
        self._email = temp_msg

    def add_html(self, html):
        temp_msg = self._email
        temp_msg.add_alternative(html, subtype='html')

    def add_attach(self, file_path):
        temp_msg = self._email
        content_type, encoding = mimetypes.guess_type(file_path)
        temp_maintype, temp_subtype = content_type.split('/', 1)
        temp_filename = PurePath(file_path).name
        with open(file_path, 'rb') as fp:
            temp_msg.add_attachment(fp.read(), maintype=temp_maintype, subtype=temp_subtype, filename=temp_filename)

    def add_excel(self, file, filename=None):
        temp_msg = self._email
        temp_name = filename if filename else self._filename
        temp_msg.add_attachment(file.getvalue(), maintype=self._maintype, subtype=self._subtype, filename=temp_name)

    def send(self, auth_user='xxxxx', auth_pass='kkkkkk'):
        temp_server = smtplib.SMTP_SSL(self._smtp_server, self._smtp_port)
        temp_server.login(auth_user, auth_pass)
        with temp_server as smtp:
            smtp.helo()
            smtp.send_message(self._email)
        logging.info("邮件发送成功")
