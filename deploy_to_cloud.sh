gcloud auth login

gcloud builds submit --config build.yaml

gcloud run deploy gpt-api --region=us-central1 --allow-unauthenticated --image=us-central1-docker.pkg.dev/aerobic-gantry-387923/gptapi/fastapi