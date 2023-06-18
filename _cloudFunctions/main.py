import base64

import json

from predict import returnPrediction
from cloudevents.http import CloudEvent
import functions_framework

from bson import json_util

from google.api_core.exceptions import FailedPrecondition

from pymongo.mongo_client import MongoClient
from collections.abc import MutableMapping
uri = "mongodb+srv://ndan0112:mqbgMMhH1i2lyD2t@promptgpt.zkajoet.mongodb.net/?retryWrites=true&w=majority"




# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def subscribe(cloud_event: CloudEvent) -> None:
    # Create a new client and connect to the server
    client = MongoClient(uri)
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
    except FailedPrecondition as error:
        collection.update_one(
        {'token': token},
        {'$set': {'prediction': "Vertex AI Server is down. Try again later!"}}
        )
        return ("", 204)
    #get revised answer


    collection.update_one(
        {'token': token},
        {'$set': {'prediction': prediction}}
    )


    # # Acknowledge the Pub/Sub message
    return ("", 204)