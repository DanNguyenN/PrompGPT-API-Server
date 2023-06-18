import base64

import json

from predict import returnPrediction
from cloudevents.http import CloudEvent
import functions_framework

from bson import json_util

from google.api_core.exceptions import FailedPrecondition
from google.cloud import pubsub_v1


from pymongo.mongo_client import MongoClient
from collections.abc import MutableMapping
uri = "mongodb+srv://promptgpt.zkajoet.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
# Create a new client and connect to the server

project_id = "aerobic-gantry-387923"
topic_id = "promptgpt"
subscription_id = "promptgpt-sub"

def acknowledgeMessage(ack_id):
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        project_id, subscription_id
    )
    try:
        subscriber.acknowledge(
            request={"subscription": subscription_path, "ack_ids": [ack_id]}
        )
    except:
        pass
    print("acknowledged message")
    return ("", 204)


# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def subscribe(cloud_event: CloudEvent) -> None:
    # Create a new client and connect to the server
    client = MongoClient(uri,
                     tls = True,
                     tlsCertificateKeyFile = "MongoDB.pem")
    # Init the collection
    db = client['predictions']
    collection = db['predictions_collection']
    # Print out the data from Pub/Sub, to prove that it worked
    # Decode the Base64-encoded data from Pub/Sub message
    data = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
    print("received data", data) #received data {"messages": [{"data": "abcd2", "attributes": {"token": "c0e0dddf-bbfc-4390-8fff-a21d1f008fa9"}}]}
    
    
    # Extract the token from Pub/Sub message attributes
    token = json.loads(data)["messages"][0]["attributes"]["token"]
    text = json.loads(data)["messages"][0]["data"]

    
    existToken = collection.find_one({'token': token})
    if existToken:
        if existToken['prediction'] != "not ready":
            print("token already exists and is already processed")
            return ("", 204)
    else:
        return("", 204)
    # Process the data and get the prediction
    
    try:
        prediction = returnPrediction(text)#it return {"predictions": [{"revised": answer}]}
        print(prediction)
        #get revised answer
        collection.update_one(
            {'token': token},
            {'$set': {'prediction': prediction}}
        )
        return ("", 204)
    except FailedPrecondition as error:
        collection.update_one(
        {'token': token},
        {'$set': {'prediction':  [{"revised": "GPU server is currently offline. Please try again later."}]}}
        )
        return ("", 204)
    
    # unacknowledge the Pub/Sub message

        

    