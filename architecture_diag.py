from optparse import IndentedHelpFormatter
from diagrams import Cluster, Diagram, Edge
from diagrams.programming.language import Python
from diagrams.gcp.analytics import PubSub, \
    BigQuery, Dataprep, Dataflow
from diagrams.gcp.storage import Storage



with Diagram('GCP Sentiment Architecture', show=False):
    
    with Cluster('Tweet streaming'):
        tweet_producer = Python('producer script')

    with Cluster('GCP'):
        pubsub = PubSub('PubSub topic')
        dp = Dataprep('Dataprep')
        df = Dataflow('Dataflow')
        bq = BigQuery('Big Query table')
        gcs = Storage('GCS as raw tweets sink')

    tweet_producer >> pubsub 
    pubsub >> df
    df >> gcs
        