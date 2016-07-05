#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Simple RFC822 Decoder

Author: Kevin Fowlks
Date:   06/30/2016

This program reads an RFC822 file  from Google groups and extracts the first text/plain payload.

Usage:
    The program can be run as shown below:

        $ python dump_body.py <mbox input file>
"""


from email.parser import Parser
import email
import sys

def get_decoded_email_body(message_body):
    """ Decode email body.

    Detect character set if the header is not set.

    We try to get text/plain, but if there is not one then fallback to text/html.

    :param message_body: Raw 7-bit message body input e.g. from imaplib. Double encoded in quoted-printable and latin-1

    :return: Message body as unicode string
    """

    msg = email.message_from_string(message_body)

    text = ""
    if msg.is_multipart():
        html = None
        for part in msg.get_payload():

            print "%s, %s" % (part.get_content_type(), part.get_content_charset())

            if part.get_content_charset() is None:
                # We cannot know the character set, so return decoded "something"
                text = part.get_payload(decode=True)
                continue

            charset = part.get_content_charset()
            #if part.get_content_charset() is not None else charset = 'utf-8'

            if part.get_content_type() == 'text/plain':
                text = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')

            if part.get_content_type() == 'text/html':
                html = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')
            
        if text is not None:
            return text.strip()
        else:
            return html.strip()
    else:
        text = unicode(msg.get_payload(decode=True), 'utf8', 'ignore').encode('utf8', 'replace')
        return text.strip()


def main():
    pass


inputFile = sys.argv[1]
#  If the e-mail headers are in a file, uncomment this line:
headers = Parser().parse(open(inputFile, 'r'))

#  Now the header items can be accessed as a dictionary:
print 'To: %s' % headers['to']
print 'From: %s' % headers['from']
print 'Subject: %s' % headers['subject']

if headers.is_multipart():
    for payload in headers.get_payload():
        if payload.get_content_type() == 'text/plain':
            print get_decoded_email_body(payload.get_payload())

if __name__ == '__main__':
    main()


