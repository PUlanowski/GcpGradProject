
from google.cloud import bigquery
from google.cloud import language_v1
import schedule
import time
from datetime import datetime


def sentiment():
    """This method gets BQ table text field along with id for further processing. Then pass text to Natural Language API and save response to final sentiment BQ table. During first BQ table fetch already analyzed tweets are filtered out.
    """    
    bqclient = bigquery.Client(project='piotr-ulanowski-sandbox-1')
    client = language_v1.LanguageServiceClient()


    query_string1 = """
    SELECT p.tweet_id, tweet_text FROM `piotr-ulanowski-sandbox-1.tweet_sentiment.tweets_processed` AS p
    LEFT JOIN `piotr-ulanowski-sandbox-1.tweet_sentiment.tweets_sentiment` AS s
    ON p.tweet_id = s.tweet_id
    WHERE s.tweet_id IS NULL
    """
    result = bqclient.query(query_string1)
    rows = list(result.result(max_results=20)) #narrowing result to 20 records for testing purposes

    for row in rows:
        
        text = str(row.values()[1])
        #print(text)
        #print(type(text))

        document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
        sentiment = client.analyze_sentiment(request={"document": document}).document_sentiment

        sentiment_score = sentiment.score
        sentiment_magnitude = sentiment.magnitude
        print("Sentiment,Magnitude: {}, {}".format(sentiment.score, sentiment.magnitude))
        tweet_id = row.values()[0]

        query_string2 = """
        INSERT INTO `piotr-ulanowski-sandbox-1.tweet_sentiment.tweets_sentiment`(tweet_id,sentiment_score, sentiment_magnitude) VALUES ('{}', {}, {})""".format(tweet_id,sentiment_score,sentiment_magnitude)

        bqclient.query(query_string2)
        now = datetime.now().time()
        print('sentiment item:',tweet_id,'uploaded at: ', now)

schedule.every(3).seconds.do(sentiment) # 3 sec for testing! for production flow there will be 5-10 mins intervals.

while True:
    schedule.run_pending()
    time.sleep(1)

def main():
    sentiment()

if __name__ == "__main__":
    main() 