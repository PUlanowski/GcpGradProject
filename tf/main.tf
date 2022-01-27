terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
}

#config default project
resource "null_resource" "health_check" {
    
    provisioner "local-exec" {
        command = "gcloud config set project ${var.project}"
    }
} 

#Creating GCS bucket
resource "google_storage_bucket" "dataflow" {
  name          = "dataflow-piotr-ulanowski-sandbox-1"
  location      = "US"
  force_destroy = true
  project = var.project
  }

#Creating folders within bucket
resource "google_storage_bucket_object" "temp" {
  name          = "temp/"
  bucket        = var.bucket
  content = "empty"
  depends_on = [google_storage_bucket.dataflow]
}

resource "google_storage_bucket_object" "tweets" {
  name          = "tweets/"
  bucket        = var.bucket
  content = "empty"
  depends_on = [google_storage_bucket.dataflow]
}
#Creating PubSub topic & subscription
resource "google_pubsub_topic" "twitt_stream" {
  name = "twitt_stream"
  project = var.project
  message_retention_duration = "86400s"
}

resource "google_pubsub_subscription" "twitt_stream-sub" {
  name  = "twitt_stream-sub"
  topic = google_pubsub_topic.twitt_stream.name
  depends_on = [google_pubsub_topic.twitt_stream]
}

#BigQuery dataset and tables

resource "google_bigquery_dataset" "tweet_sentiment" {
  dataset_id                  = "tweet_sentiment"
  description                 = "This is a test description"
  location                    = "US"
  project = var.project
  delete_contents_on_destroy = true
}
# Table tweets_raw
resource "google_bigquery_table" "tweets_raw" {
  dataset_id = "tweet_sentiment"
  table_id   = "tweets_raw"
  deletion_protection=false
  schema = <<EOF
[
    {
        "name": "tweet_id",
        "type": "STRING",
        "mode": "NULLABLE"
    },
    {
        "name": "tweet_created_at",
        "type": "STRING",
        "mode": "NULLABLE"
    }, 
    {
        "name": "tweet_lang",
        "type": "STRING",
        "mode": "NULLABLE"
    }, 
    {
        "name": "tweet_text",
        "type": "STRING",
        "mode": "NULLABLE"
    }, 
    {
        "name": "usr_descr",
        "type": "STRING",
        "mode": "NULLABLE"
    }, 
    {
        "name": "usr_id",
        "type": "STRING",
        "mode": "NULLABLE"
    }, 
    {
        "name": "usr_name",
        "type": "STRING",
        "mode": "NULLABLE"
    },   
    {
        "name": "usr_username",
        "type": "STRING",
        "mode": "NULLABLE"
    },   
    {
        "name": "tag",
        "type": "STRING",
        "mode": "NULLABLE"
    }
]
EOF
  depends_on = [google_bigquery_dataset.tweet_sentiment]
}

# Table tweets_processed
resource "google_bigquery_table" "tweets_processed" {
  dataset_id = "tweet_sentiment"
  table_id   = "tweets_processed"
  deletion_protection=false

  schema = <<EOF
[
    {
        "name": "tweet_id",
        "type": "STRING",
        "mode": "NULLABLE"
    },
    {
        "name": "tag",
        "type": "STRING",
        "mode": "NULLABLE"
    },
    {
        "name": "tweet_text",
        "type": "STRING",
        "mode": "NULLABLE"
    },
    {
        "name": "tweet_year",
        "type": "INTEGER",
        "mode": "NULLABLE"
    },
    {
        "name": "tweet_month",
        "type": "INTEGER",
        "mode": "NULLABLE"
    },
    {
        "name": "tweet_day",
        "type": "INTEGER",
        "mode": "NULLABLE"
    }
]
EOF
  depends_on = [google_bigquery_dataset.tweet_sentiment]
}

# Table tweets_sentiment
resource "google_bigquery_table" "tweets_sentiment" {
  dataset_id = "tweet_sentiment"
  table_id   = "tweets_sentiment"
  deletion_protection=false

  schema = <<EOF
[
    {
        "name": "tweet_id",
        "type": "STRING",
        "mode": "NULLABLE"
    },
    {
        "name": "sentiment_score",
        "type": "FLOAT",
        "mode": "NULLABLE"
    },
    {
        "name": "sentiment_magnitude",
        "type": "FLOAT",
        "mode": "NULLABLE"
    }
]
EOF
  depends_on = [google_bigquery_dataset.tweet_sentiment]
}

#Dataflow jobs
resource "google_dataflow_job" "pubsub-to-gcs-avro" {
    name = "pubsub-to-gcs-avro"
    template_gcs_path = "gs://dataflow-templates-us-central1/latest/Cloud_PubSub_to_Avro"
    temp_gcs_location = "gs://dataflow-piotr-ulanowski-sandbox-1/tweets/tweet-dump"
    region = var.region
    max_workers = 2
    parameters = {
      inputTopic = var.inputTopic
      outputDirectory = "gs://${var.bucket}/tweets"
      avroTempDirectory = "gs://${var.bucket}/temp"
    }
    on_delete = "cancel"
    depends_on = [google_storage_bucket_object.tweets, google_storage_bucket_object.temp, google_pubsub_topic.twitt_stream ]
}

resource "google_dataflow_job" "pubsub-to-bq" {
    name = "pubsub-to-bq"
    template_gcs_path = "gs://dataflow-templates-us-central1/latest/PubSub_to_BigQuery"
    temp_gcs_location = "gs://dataflow-piotr-ulanowski-sandbox-1/tweets/tweet-dump"
    region = var.region
    max_workers = 2
    parameters = {
      inputTopic = var.inputTopic
      outputTableSpec = var.outputTable
    }
    on_delete = "cancel"
    depends_on = [google_pubsub_topic.twitt_stream, google_bigquery_table.tweets_raw]
}