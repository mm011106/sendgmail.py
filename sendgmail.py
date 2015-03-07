#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  sendmail.py: 
#       send gmail with pdf attachment
#   option:
#      -l, --list : recipient list file  (one e-mail address par one line)
#      -a, --attach : file name to be attached on the e-mail 
#           !! Regular expression is not acceptable !!
#
#   V1.0 2015/03/07   M.Miyamoto
#      refer to http://qiita.com/ssh0/items/7baa0cd094d9fb7561e1


import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.Header import Header
from email.MIMEBase import MIMEBase
from email.Utils import formatdate
from email import Encoders
from platform import python_version
import argparse
import getpass
import codecs
import re
import os

release = python_version()
if release > '2.6.2':
    from smtplib import SMTP_SSL
else:
    SMTP_SSL = None

def create_message(from_addr, sender_name, to_addr, subject, body, encoding):
#    msg = MIMEText(body, 'plain', encoding)
    msg = MIMEMultipart()
    msg['Subject'] = Header(subject, encoding)
    form_jp = u"%s <%s>" % (str(Header(sender_name, encoding)), from_addr)
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Date'] = formatdate()
    body = MIMEText(body, 'plain', encoding )
    msg.attach(body) 
    return msg

def send_via_gmail(from_addr, to_addr, passwd, msg):
    if SMTP_SSL:
        s = SMTP_SSL('smtp.gmail.com', 465)
        s.login(from_addr, passwd)
        s.sendmail(from_addr, to_addr, msg.as_string())
        s.close()
        print 'mail sent via SSL!'
    else:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        if release < '2.6':
            s.ehlo()
        s.starttls()
        if release < '2.5':
            s.ehlo()
        s.login(from_addr, passwd)
        s.sendmail(from_addr, to_addr, msg.as_string())
        s.close()
        print "mail sent via TLS."

def rstrip(s):
    return s.rstrip()

def read_recipients_list(file_name):

    with open(file_name) as file:
        address=file.readlines()

    #  remove \n at the last of each element
    address_list=map(rstrip,address)

    #  reject comment lines and NULL lines
    p1 = re.compile("^\s*#")
    p2 = re.compile("^\s*$")

    address_list= [x for x in address_list if p1.match(x) == None ]
    address_list= [x for x in address_list if p2.match(x) == None ]
    
    return address_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send a email with attachment PDF file via Gmail.')
    parser.add_argument('-l', '--list', dest='recipients_list_file', type=str,
                        default='./recipients_list_default',
                        help='[To] address list file name')
    parser.add_argument('-a', '--attach', dest='attach_file', type=str,
                        default=None , help='PDF file name to be attached')
    args = parser.parse_args()

    SEPARATOR = ', '

    from_addr   = "from@my.account.jp"
    sender_name =u'your name here'
#    print "from: %s <%s>" % (sender_name, from_addr)
#   passwd = getpass.getpass()
#   
    passwd = "password here"

    if os.path.exists(args.recipients_list_file):    
        #  extract basename form the file name
        site_id = os.path.basename(args.recipients_list_file)
        #  reject extension of the file name
        site_id = os.path.splitext(site_id)[0]
        r = re.compile('[0-9]+')     # Extract number in the filenam = site number
        matched = r.search(site_id)

        if matched != None:
            site_no = matched.group(0) 
        else:
            site_no = 'NO ID'
    
#    pass sendmail command the recipients list as a LIST
        to_addr=read_recipients_list(args.recipients_list_file)

    else:
        print ('No recipients list was found. Use default e-mail address.')
        site_no = 'Default'
        to_addr = ['default.email@my.account.jp']



#    pass msg object the recipients list in the header as a joined string
    to_addr_header=SEPARATOR.join(to_addr)

#    tite of the msg 
    title = subject = ('title of the message' + site_no )

#    body message of the msg
    body =  \
"""
You can place your message here.

Thanks,

"""

#   prepare PDF file as a attachemnt
    attach_file_name = args.attach_file

    if attach_file_name != None :
        if os.path.exists(attach_file_name) :
            attachment = MIMEBase("application","pdf")

            with open(args.attach_file, 'rb') as fp:
                attachment.set_payload(fp.read())
    
            Encoders.encode_base64(attachment)
            base_file_name = os.path.basename(attach_file_name)
            attachment.add_header("Content-Disposition", "attachment", filename=base_file_name)
        else:
            print ('No attachment file is found.')
    else:
       print ('No attachment file is specified.')

#
#  check number of recipients in the list

    if len(to_addr)!=0 : 
        #   make msg object    
        msg = create_message(from_addr, sender_name, to_addr_header, title, body, 'utf-8')

        #     attach the PDF file
        if 'attachment' in locals():
            msg.attach(attachment)

        #   send meg object via gmail   
        send_via_gmail(from_addr, to_addr, passwd, msg) 
   
    else:
        print "No recipient was found."


