# -*- encoding: utf-8 -*-

import sys
import os

import base64
from email.message import EmailMessage

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class GMail():
    def __init__(self, token):
        print("Connecting Gmail")
        if token:
            self.creds = Credentials.from_authorized_user_info(token, SCOPES)
        else:
            self.creds = None
        if not self.creds or not self.creds.valid:
            print("Token not exist/valid")
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("Refresh token")
                self.creds.refresh(Request())
            else:
                print("download token")
                flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
                creds = self.creds.to_json()
                print(creds)
                with open("credentials.json", "w") as f:
                    f.write(creds)

#        print(self.creds.to_json())
        self.service = build('gmail', 'v1', credentials=self.creds)

    def SendMessage(self, user_id, message):
        """Send an email message.

        Args:
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          message: Message to be sent.

        Returns:
          Sent Message.
        """
        try:
            message = (self.service.users().messages().send(userId=user_id, body=message)
                       .execute())
            print('Message Id: %s' % message['id'])
            return message
        except HttpError as error:
            print('An error occurred: {}'.format(error))

    def CreateMessage(self, sender, to, subject, message_text):
        """Create a message for an email.

        Args:
          sender: Email address of the sender.
          to: Email address of the receiver.
          subject: The subject of the email message.
          message_text: The text of the email message.

        Returns:
          An object containing a base64url encoded email object.
        """
        message = EmailMessage()
        message['To'] = to
        message['From'] = sender
        message['Subject'] = subject
        message.set_content(message_text)

        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

