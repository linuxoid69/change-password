import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Email(object):
    def __init__(self, smtphost, port, username, passwd):
        """
        :param smtphost: smtp host
        :param port: smtp port
        :param username:  login
        :param passwd:  password
        """
        self.smtphost = smtphost
        self.port = port
        self.username = username
        self.passwd = passwd
        self.server = smtplib.SMTP_SSL(smtphost, port)
        self.server.login(username, passwd)

    def send_mail(self, sender, recipients, subj, msg_html):
        """
        :param sender:
        :param recipients:
        :param subj:
        :param msg_html:
        """
        self.msg = MIMEMultipart('alternative')
        self.msg['Subject'] = subj
        self.msg['From'] = sender
        self.msg['To'] = recipients
        self.msg['Reply-To'] = sender
        self.part = MIMEText(msg_html, 'html')
        self.msg.attach(self.part)
        self.server.sendmail(sender, recipients, self.msg.as_string())
        self.server.quit()
