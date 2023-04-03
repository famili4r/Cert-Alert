#!/usr/bin/python3

from cryptography import x509
import ssl
import os
import csv
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#requires pip install python-dotenv
from dotenv import load_dotenv


load_dotenv()
#setup SMTP settings to .env file
SMTP_SERVER = os.getenv('SMTP_SERVER')
SENDER = os.getenv('SENDER')
RECEIVER = os.getenv('RECEIVER')
SMTP_PORT = os.getenv('SMTP_PORT')


#Server list should be a text file with each server on it's own row with the port separated with a space.
#Define the location of the file in the .env
#Syntax example:
# server1.com 443
# server2.com 443
# server3.com 8443

SERVER_LIST = os.getenv('SERVER_LIST')


def main():
   
    with open(SERVER_LIST) as load_file:
        reader = csv.reader(load_file, delimiter=" ")
        data = [tuple(row) for row in reader]
        servers, ports = zip(*data)


    today = datetime.datetime.now().date()
    delta = datetime.timedelta(days = 14)
    alertdate = today + delta


    for server, port in zip(servers, ports):
        certdata = bytes((ssl.get_server_certificate((server, port))), 'UTF-8')
        cert = x509.load_pem_x509_certificate(certdata)
        expdate = cert.not_valid_after.date()

        if expdate >= alertdate:

            message = MIMEMultipart("alternative")
            message["Subject"] = server + " Certificate expiring soon!"
            message["From"] = SENDER
            message["To"] = RECEIVER
            
            text = server + ' certificate is expiring soon, ' + str(expdate)
            part1 = MIMEText(text, "plain")
            message.attach(part1)
            email = smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT))
            email.sendmail(SENDER, RECEIVER, message.as_string())

 
main()

