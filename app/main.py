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

from bson import json_util

from pymongo.mongo_client import MongoClient
uri = "mongodb+srv://promptgpt.zkajoet.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri,
                     tls = True,
                     tlsCertificateKeyFile = "/app/MongoDB.pem")
# Init the collection
db = client['predictions']
collection = db['predictions_collection']

project_id = "aerobic-gantry-387923"
topic_id = "promptgpt"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)


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
    token_length = 32

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

    collection.insert_one({'token': token, 'input': text,'prediction': "not ready"})

    #publish to server pubsub
    future = publisher.publish(topic_path, data=json.dumps(data).encode("utf-8"))
    
    # Wait for the message to be published
    future.result()


    print("Request published to Pub/Sub.")
    return {"token": token}

@app.get("/result/{token}")
async def result(token: str):
    result = collection.find_one({'token': token})
    if result: 
        if result['prediction'] == "not ready":
            query = {"prediction": "not ready"}
            #Get the index of result
            results = collection.find(query)
            document_list = list(results)
            result_index = document_list.index(result)
            # Get the length of the results
            result_count = collection.count_documents(query)
            return {"position": result_index + 1, "queueSize": result_count}
        
        return json.loads(json_util.dumps(result))
    else:
        raise HTTPException(status_code=404, detail="Invalid Token")
    
    
        

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), proxy_headers=False, workers=1)
    
