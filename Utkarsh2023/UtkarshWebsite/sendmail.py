import os
import pickle
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type
# Request all access (permission to read/send/receive emails, manage the inbox, and more)

class SendEmail():
    def __init__(self,provider,our_email):
        self.provider = provider
        self.our_email = our_email
        
    def gmail_authenticate(self):
        creds = None
        # the file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time
        if os.path.exists("creds/token.pickle"):
            with open("creds/token.pickle", "rb") as token:
                creds = pickle.load(token)
        # if there are no (valid) credentials availablle, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('creds/credentials.json', self.provider)
                creds = flow.run_local_server(port=0)
            # save the credentials for the next run
            with open("creds/token.pickle", "wb") as token:
                pickle.dump(creds, token)
        return build('gmail', 'v1', credentials=creds)
   
   
    def build_message(self, destination, obj, body):
        message = MIMEText(body)
        message['to'] = destination
        message['from'] = self.our_email
        message['subject'] = obj
        return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}


    def send_message(self, service, destination, obj, body):
        return service.users().messages().send(
          userId="me",
          body=self.build_message(destination, obj, body)
        ).execute()
        
