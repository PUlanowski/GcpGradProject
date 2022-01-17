gcloud dataflow jobs run  pubsub-to-gcs2 --gcs-location gs://dataflow-templates-us-central1/latest/Cloud_PubSub_to_GCS_Text --region us-central1 --staging-location gs://dataflow-temp-piotr-ulanowski-sandbox-1/temp/ --parameters inputTopic=projects/piotr-ulanowski-sandbox-1/topics/twitt_stream,outputDirectory=gs://dataflow-temp-piotr-ulanowski-sandbox-1/tweets/,outputFilenamePrefix=tweet-

