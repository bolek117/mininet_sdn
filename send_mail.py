#!/usr/bin/env python

__author__ = 'jblaszczyk'

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders

def parse_args():
    parser = ArgumentParser()

    parser.add_argument('-s', '--sender', type=str, default='host1@localhost', dest='send_from',
                        help='Email address of the sender')
    parser.add_argument('-r', '--reciver', type=str, default='host2@localhost', dest='send_to',
                        help='Email address of the reciver')
    parser.add_argument('-t', '--text', type=str, default='testmail.txt', dest='textfile',
                        help='Email text content')
    parser.add_argument('-f', '--file', type=str, default=None, dest='sendfile',
                        help='Email address of the reciver')
    
    return parser.parse_args()

def send_mail(send_from, send_to, subject, text, files=None,
              server="127.0.0.1"):
    assert isinstance(send_to, list)

if __name__ = '__main__':
  args = parse_args()

  msg = MIMEMultipart()
  msg['Subject'] = textfile 
  msg['From'] = send_from
  msg['To'] = send_to
  
  if args.sendfile is not None:
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(sendfile, "rb").read())
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="text.txt"')
    msg.attach(part)

  server = smtplib.SMTP(self.EMAIL_SERVER)
  server.sendmail(self.EMAIL_FROM, self.EMAIL_TO, msg.as_string())








    

    