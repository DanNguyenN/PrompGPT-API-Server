import base64

import uuid
import json
from google.cloud import pubsub_v1

from predict import returnPrediction
from cloudevents.http import CloudEvent
import functions_framework

project_id = "aerobic-gantry-387923"
topic_id = "promptgpt-result"
publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()

subscription_path = "projects/aerobic-gantry-387923/subscriptions/promptgpt-sub"

# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def subscribe(cloud_event: CloudEvent) -> None:
    # Print out the data from Pub/Sub, to prove that it worked
    # Decode the Base64-encoded data from Pub/Sub message
    data = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
    print("received data", data) #received data {"messages": [{"data": "abcd2", "attributes": {"token": "c0e0dddf-bbfc-4390-8fff-a21d1f008fa9"}}]}
    
    # Extract the token from Pub/Sub message attributes
    token = json.loads(data)["messages"][0]["attributes"]["token"]
    text = json.loads(data)["messages"][0]["data"]

    # Process the data and get the prediction
    prediction = returnPrediction(text)#it return {"predictions": [{"revised": answer}]}
    print(prediction)
    #get revised answer

    # Create a new message with the prediction and token
    results = {
        "messages": [
            {
                "data": prediction,
                "attributes": {
                    "token": token
                }
            }
        ]
    }

    # Publish the result to a new Pub/Sub topic
    topic_path = publisher.topic_path(project_id, topic_id)
    future = publisher.publish(topic_path, data=json.dumps(results).encode("utf-8"))

    # Wait for the message to be published
    future.result()

    # #  Acknowledge the message
    # print(data)
    # ack_ids = json.loads(data)["ackId"]
    # try:    
    #     subscriber.acknowledge(request={
    #         'subscription': subscription_path,
    #         'ack_ids': ack_ids,
    #     })
    # except:
    #     print("Acknowledge Failed")
    #     pass

    # # Acknowledge the Pub/Sub message
    return ("", 204)