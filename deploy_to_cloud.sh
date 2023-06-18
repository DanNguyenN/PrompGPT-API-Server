gcloud auth login

gcloud builds submit --config build.yaml

gcloud run deploy gpt-api --region=us-central1 --allow-unauthenticated --image=us-central1-docker.pkg.dev/aerobic-gantry-387923/gptapi/fastapi --max-instances=1


#To deploy to cloud functions
gcloud functions deploy python-pubsub-function --gen2 --max-instances=1 --runtime=python310 --region=us-central1 --source=_cloudFunctions/. --entry-point=subscribe --trigger-topic=promptgpt --set-env-vars=[GOOGLE_APPLICATION_CREDENTIALS=very_important_key.json]