# -*- coding: utf-8 -*-
"""
@author: Ye Shengnan
create: 2018-05-16
"""
import smtplib
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class MailClient(object):
    def __init__(self, smtp_server, smtp_port, username, passwd, from_mail, from_name):
        self._smtp_server = smtp_server
        self._smtp_port = smtp_port
        self._username = username
        self._passwd = passwd
        self._from_mail = from_mail
        self._from_name = from_name

    def send(self, to, subject, content, attachment=None, cc=None, bcc=None):
        """
        content:
            [
                'this is a text',
                ('picture1.png', picture_bytes, 'http://www.baidu.com'),
                'this is another text'
            ]

        attachment:
            [
                ('image', 'picture1.png', picture_bytes)
            ]
        """
        sm = smtplib.SMTP(self._smtp_server, self._smtp_port, timeout=20)
        sm.set_debuglevel(1)
        if self._smtp_port > 200:
            sm.starttls()
        sm.ehlo()
        sm.ehlo()
        sm.login(self._username, self._passwd)

        tos = to[:]
        if cc is not None:
            tos.extend(cc)
        if bcc is not None:
            tos.extend(bcc)

        msg = self._build_message(to, subject, content, attachment, cc, bcc)
        senderrs = sm.sendmail(self._from_mail, tos, msg.as_string())
        sm.quit()

        return senderrs

    def _simple_html(self, items):
        text = ''
        for index, item in enumerate(items):
            if index != 0:
                text += '<br />'
            if type(item) in (list, tuple):
                tag = ('<img alt="" src="cid:%s" />' % item[0])
                if item[2] is not None:
                    text += ('<a href="%s">%s</a>' % (item[2], tag))
                else:
                    text += tag
            else:
                text += item
        msg_text = MIMEText(text, 'html', 'utf-8')
        return msg_text

    def _build_message(self, to, subject, content, attachment, cc, bcc):
        msg_root = MIMEMultipart('related')
        msg_root['Subject'] = subject
        h = Header(self._from_name, 'utf-8')
        h.append('<%s>' % self._from_mail, 'ascii')
        msg_root['From'] = h
        msg_root['To'] = ','.join(to)
        if cc is not None:
            msg_root['Cc'] = ','.join(cc)
        if bcc is not None:
            msg_root['Bcc'] = ','.join('bcc')

        if type(content) in (list, tuple):
            msg_root.attach(self._simple_html(content))
            for c in content:
                if type(c) in (list, tuple):
                    item = MIMEImage(c[1])
                    item.add_header('Content-ID', c[0])
                    msg_root.attach(item)
        else:
            msg_root.attach(MIMEText(content, 'plain', 'utf-8'))

        if attachment is not None:
            for att in attachment:
                item = None
                if att[0] == 'image':
                    item = MIMEImage(att[2])
                    item.add_header('Content-ID', att[1])
                if item is not None:
                    msg_root.attach(item)

        return msg_root
