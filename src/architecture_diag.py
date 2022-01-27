from optparse import IndentedHelpFormatter
from diagrams import Cluster, Diagram, Edge
from diagrams.programming.language import Python
from diagrams.gcp.analytics import PubSub, \
    BigQuery, Dataflow, Dataprep
from diagrams.gcp.storage import Storage
from diagrams.generic.device import Tablet, Mobile
from diagrams.onprem.iac import Terraform
from diagrams.gcp.compute import ComputeEngine
from diagrams.gcp.ml import NaturalLanguageAPI

with Diagram('GCP Tweets Sentiment Architecture', show=False):

    tf = Terraform('build infra on GCP')
    tweet_producer = Python('streaming tweets')
    tweet_sentiment = Python('sentiment ETL')
    ds = Tablet('Data Studio charts')
        
    with Cluster('GCP'):

        with Cluster('IaC'):
            #tf = Terraform('build infra on GCP')
            gce = ComputeEngine('Cloud Shell')        
        
        with Cluster ('Big Query'):
            bq1 = BigQuery('tweets_raw')
            bq2 = BigQuery('tweets_processed')
            bq3 = BigQuery('tweets_sentiment')

        with Cluster("Natural LAnguage API"):
            nlapi = NaturalLanguageAPI('sentiment analysis')
        
        pubsub = PubSub('PubSub topic')
        df = Dataflow('Dataflow')
        gcs = Storage('GCS tweets Avro sink')
   

    with Cluster('Dataprep'):
        dp = Dataprep('scheduled job')

        


    tf >> Edge(color="purple") >>gce
    tweet_producer >>  Edge(color="orange") >> pubsub
    pubsub >>  Edge(color="orange") >> df
    df >> Edge(color="orange") >> gcs
    df >>  Edge(color="orange") >> bq1 >> Edge(color="orange") >> dp
    dp >> Edge(color="orange") >> bq2
    bq2 >> Edge(color="orange") >> ds
    bq2 >> Edge(color="darkgreen") >> tweet_sentiment
    tweet_sentiment - Edge(color="darkgreen", style="dashed") >> nlapi
    nlapi - Edge(color="darkgreen", style="dashed") >> tweet_sentiment
    tweet_sentiment >> Edge(color="darkgreen") >> bq3    

