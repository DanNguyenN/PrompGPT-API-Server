<<<<<<< Updated upstream
# [START aiplatform_predict_custom_trained_model_sample]
from typing import Dict, List, Union
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
# from prompt_optimizer.poptim import EntropyOptim

=======
>>>>>>> Stashed changes
import os
from fastapi import FastAPI
<<<<<<< Updated upstream
# p_optimizer = EntropyOptim(verbose=True, p=0.1)

app = FastAPI()
=======
from fastapi.middleware.cors import CORSMiddleware
from predict import returnPrediction
import uvicorn
import asyncio

from google.cloud import pubsub_v1

app = FastAPI()

>>>>>>> Stashed changes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
<<<<<<< Updated upstream
    allow_headers=["*"]
)
=======
    allow_headers=["*"],
)

predict_lock = asyncio.Lock()
route_check_lock = asyncio.Lock()
predict_running = False
>>>>>>> Stashed changes

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/status")
async def route_check():
    return {"available": not predict_running}


@app.get("/predict/{text}")
async def predict(text: str):
<<<<<<< Updated upstream
    return predict_custom_trained_model_sample(
    project="569587263363",
    endpoint_id="9073376660593573888",
    location="us-central1",
    # instances={ "text": p_optimizer(text)},
    instances={ "text": text}
)
=======
    global predict_running
    async with predict_lock:
        predict_running = True
        try:
            return returnPrediction(text)
        finally:
            predict_running = False


>>>>>>> Stashed changes
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), workers=1, proxy_headers=False)
