import boto3
import json
import os

session = boto3.session.Session()

class SQSClient:

    def __init__(self, sqsConfig):
        self.sqs = session.client(
            'sqs',
            region_name = sqsConfig["REGION"],
            endpoint_url = sqsConfig["URL"],
            aws_access_key_id = sqsConfig["ACCESS_KEY"],
            aws_secret_access_key = sqsConfig["SECRET_ACCESS_KEY"]
        )
        self.URL = sqsConfig["URL"]

        print("SQSClient initialized")

    def PopQueue(self, reqCount = 0):

        if reqCount == 0:
            count = 10;
        else:
            count = reqCount

        msgs = list()
        while True:
            response = self.sqs.receive_message(
                QueueUrl=self.URL,
                AttributeNames=[""],
                MaxNumberOfMessages=count,
                MessageAttributeNames=['All'],
                VisibilityTimeout=5,
                WaitTimeSeconds=5,
            )
            count = len(response['Messages']) if 'Messages' in response else 0
            print(f"receive done {count}")
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
                        QueueUrl=self.URL,
                        ReceiptHandle=receipt_handle
            )

            if count == 0 or reqCount == count:
                break

        print(f"Total {len(msgs)} message(s) read")
        return msgs

if __name__ == "__main__":
    client = SQSClient()

    msg = client.PopQueue()

    print(msg)

