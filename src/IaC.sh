#Get data from PubSub and parse to GCS as Avro files with tweets from 5 mins windows
gcloud dataflow jobs run pubsub-to-gcs-avro --gcs-location gs://dataflow-templates-us-central1/latest/Cloud_PubSub_to_Avro --region us-central1 --max-workers 2 --num-workers 1 --staging-location gs://dataflow-piotr-ulanowski-sandbox-1/tweets/tweet-dump- --parameters inputTopic=projects/piotr-ulanowski-sandbox-1/topics/twitt_stream,outputDirectory=gs://dataflow-piotr-ulanowski-sandbox-1/tweets,avroTempDirectory=gs://dataflow-piotr-ulanowski-sandbox-1/temp

#PubSub stream to BQ
gcloud dataflow jobs run pubsub-to-bq --gcs-location gs://dataflow-templates-us-central1/latest/PubSub_to_BigQuery --region us-central1 --max-workers 2 --num-workers 1 --staging-location gs://dataflow-piotr-ulanowski-sandbox-1/temp --parameters inputTopic=projects/piotr-ulanowski-sandbox-1/topics/twitt_stream,outputTableSpec=piotr-ulanowski-sandbox-1:tweet_sentiment.tweets-raw

#credentials to use for Natural Language API
gcloud config set project $PROJECT
gcloud auth application-default login
gcloud auth application-default set-quota-project $PROJECT

