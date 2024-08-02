import boto3
import json
import os

REGION = "us-west-1"
URL = "https://sqs.us-west-1.amazonaws.com/088564131385/HKMCCLibraryRequest.fifo"

session = boto3.session.Session()

class SQSClient:

    def __init__(self):
        if "ACCESS_KEY" in os.environ:
            ACCESS_KEY = os.environ["ACCESS_KEY"]
        else:
            from config import Config
            ACCESS_KEY = Config["access_key"]

        if "SECRET_ACCESS_KEY" in os.environ:
            SECRET_ACCESS_KEY = os.environ["SECRET_ACCESS_KEY "]
        else:
            SECRET_ACCESS_KEY = Config["secret_access_key"]
        self.sqs = session.client(
            'sqs',
            region_name = REGION,
            endpoint_url = URL,
            aws_access_key_id = ACCESS_KEY,
            aws_secret_access_key = SECRET_ACCESS_KEY
        )

        print("SQSClient initialized")

    def PopQueue(self, count = 0):

        if count == 0:
            count = 10;

        response = self.sqs.receive_message(
            QueueUrl=URL,
            AttributeNames=[""],
            MaxNumberOfMessages=count,
            MessageAttributeNames=['All'],
            VisibilityTimeout=5,
            WaitTimeSeconds=5,
        )
        print("receive done")
        msgs = list()
        if 'Messages' in response:
            for message in response['Messages']:
                receipt_handle = message['ReceiptHandle']
        #        print(message['Body'])
                msg = dict(json.loads(message["Body"]))
                msg['_id'] = message['MessageId']
#                print(message)
                msgs.append(msg)
#                print(receipt_handle)
                self.sqs.delete_message(
                    QueueUrl=URL,
                    ReceiptHandle=receipt_handle
        )
        return msgs

if __name__ == "__main__":
    client = SQSClient()

    msg = client.PopQueue()

    print(msg)

