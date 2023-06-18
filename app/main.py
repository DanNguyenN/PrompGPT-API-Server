import os
import requests
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

import secrets
import string

import uuid
import json
from google.cloud import pubsub_v1


# Python program for the above approach.
import collections



project_id = "aerobic-gantry-387923"
topic_id = "promptgpt"

receive_topic_id = "promptgpt-result"

publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()
topic_path = publisher.topic_path(project_id, topic_id)

subscription_path = "projects/aerobic-gantry-387923/subscriptions/promptgpt-result-sub"
receivePRequest = pubsub_v1.types.PullRequest(subscription=subscription_path, max_messages=1000)

receive_topic_path = subscriber.topic_path(project_id, receive_topic_id)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_token():
    # Define the length of the token
    token_length = 16

    # Define the characters to use in the token
    characters = string.ascii_letters + string.digits

    # Generate the random token
    token = ''.join(secrets.choice(characters) for i in range(token_length))

    # Return the token 
    return token


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/predict/{text}")
async def predict(text: str):
    token = generate_token()
    data = {
        "messages": [
            {
                "data": text,
                "attributes": {
                    "token": token
                }
            }
        ]
    }
    #publish to server pubsub
    future = publisher.publish(topic_path, data=json.dumps(data).encode("utf-8"))
    
    # Wait for the message to be published
    future.result()


    print("Prediction published to Pub/Sub.")
    return {"token": token}

@app.get("/result/{token}")
async def result(token: str):

    response = subscriber.pull(receivePRequest)

    print(response)

    for received_message in response.received_messages:
        print(received_message)
        # Extract the message data and attributes
        data = received_message.message.data.decode("utf-8")
        
        
        message_token = str(json.loads(data)["messages"][0]["attributes"]["token"])
        
        print(token)
        print(message_token)
        print(token == message_token)

        # Process the message data and perform necessary operations
        if token == message_token:
            result = json.loads(data)["messages"][0]["data"]
            try: 
                subscriber.acknowledge(request={
                    'subscription': subscription_path,
                    'ack_ids': received_message.ack_id,
                })
            except:
                print("Acknowledge error")
                pass
            return result
        
        # Acknowledge the message to mark it as processed
    
    return {"prediction": "not ready", "token": token}
        

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), proxy_headers=False, workers=1)
    
