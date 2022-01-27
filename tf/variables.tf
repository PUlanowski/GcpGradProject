variable "project" {
    default = "piotr-ulanowski-sandbox-1"
 }

variable "region" {
  default = "us-central1"
}
 
variable "bucket" {
  default = "dataflow-piotr-ulanowski-sandbox-1"
}

variable "inputTopic" {
    default = "projects/piotr-ulanowski-sandbox-1/topics/twitt_stream"
}

variable "outputTable" {
    default = "piotr-ulanowski-sandbox-1:tweet_sentiment.tweets_raw"
}
