# Config

consumer_key = 'TSpnym2FzM9XJ7y1in4ZUVoCa'
consumer_secret = 'EIJ1WqdLbEUmQ1MJ4AGWu4HdHn4kggCo93e2c0uX2NCcwF7XcF'
access_token ='1481340244050038787-8GC2B5Lh9z26oBN2xmUkNKNpLISwk7'
access_token_secret = 'yj5iQvjKJ3Oe52cpR7NVOQ2kvR1d9aiLsBtA5G3CQuNCT'
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAA4qYAEAAAAAaE65KbiIHt4DFhxkoluCYwYAsSs%3DrDPABQkoH3DoKxDgg8wx5h7o7zz5NmepHlXa4LKEgAxvugXUlG'
project_id = 'piotr-ulanowski-sandbox-1'
topic_path = 'projects/piotr-ulanowski-sandbox-1/topics/twitt_stream'


from urllib import response
import requests
import os
import json
from google.cloud import pubsub_v1

# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
# bearer_token = os.environ.get("BEARER_TOKEN")


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r


def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    #print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    #print(json.dumps(response.json()))


def set_rules(delete):
    # You can adjust the rules if needed
    sample_rules = [
        {"value": "#Trump lang:en", "tag": "#trump"},
        {"value": "#Biden lang:en", "tag": "#biden"}
    ]
    
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    #print(json.dumps(response.json()))


def get_stream(set):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream", auth=bearer_oauth, stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    
    return response

def publish_pubsub(response):
    
    publisher = pubsub_v1.PublisherClient()

    for response_line in response.iter_lines():
        if response_line:
            one_tweet = str(response_line)
            json_response = json.loads(response_line)
            future = publisher.publish(topic_path, one_tweet.encode('utf-8'))
            print(f'PUBLISHED MESSAGE ID: {future.result()}')
            print(json.dumps(json_response, indent=4, sort_keys=True))



def main():
    rules = get_rules()
    delete = delete_all_rules(rules)
    set = set_rules(delete)
    response = get_stream(set)
    publish_pubsub(response)


if __name__ == "__main__":
    main()