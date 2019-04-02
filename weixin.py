# -*- coding: utf-8 -*-
"""
@author: Ye Shengnan
create: 2018-05-16
"""
import threading
import time

import itchat

# from . import email
from pyutils import email

MSG_TEXT = itchat.content.TEXT
MSG_PICTURE = itchat.content.PICTURE
MSG_ATTACHMENT = itchat.content.ATTACHMENT


class WxMsg(object):
    def __init__(self):
        self._qr_email = None
        self._message_callback = None
        self._exit_flag = False
        self._last_uuid = None

    def start(self):
        self._thread = threading.Thread(target=self._run)
        self._thread.setDaemon(True)
        self._thread.start()

    def stop(self, wait=False):
        self._exit_flag = True
        if wait and self._thread is not None and self._thread.is_alive():
            time.sleep(0.1)

    def _on_qr(self, uuid, status, qrcode):
        if uuid == self._last_uuid:
            return
        mc = email.MailClient(self._qr_email['smtp_server'], self._qr_email['smtp_port'], self._qr_email['username'],
            self._qr_email['passwd'], self._qr_email['from_mail'], self._qr_email['from_name'])
        mc.send([self._qr_email['to']], 'qrcode' + time.strftime('%Y-%m-%d %H:%M:%S'),
            [('qrcode.png', qrcode, None)])
        self._last_uuid = uuid

    def _run(self):
        while not self._exit_flag:
            cb_qr = None if self._qr_email is None else self._on_qr
            itchat.auto_login(qrCallback=cb_qr)
            itchat.run()

    def set_qr_email(self, config):
        self._qr_email = config

    def set_message_callback(self, callback):
        self._message_callback = callback

    def send_message(self, who, msg, msg_type):
        """msg_type为MSG_PICTURE或MSG_ATTACHMENT时, msg为文件路径"""
        if msg_type == MSG_TEXT:
            itchat.send(msg, name=who)
        elif msg_type == MSG_PICTURE:
            itchat.send('@%s@%s' % ('img', msg), who)
        elif msg_type == MSG_ATTACHMENT:
            itchat.send('@%s@%s' % ('fil', msg), who)

    @itchat.msg_register([itchat.content.TEXT])
    def _on_message(self, msg):
        if self._message_callback is not None:
            self._message_callback(msg)

if __name__ == '__main__':
    cfg = {
        'smtp_server': 'smtp.163.com',
        'smtp_port': 25,
        'username': 'andrewsky698',
        'passwd': 'hkrcctgrfx698',
        'from_mail': 'andrewsky698@163.com',
        'from_name': 'andrewsky698',
        'to': 'andrewsky698@163.com'
    }

    wxmsg = WxMsg()
    wxmsg.set_qr_email(cfg)
    wxmsg.start()
    time.sleep(5000)
