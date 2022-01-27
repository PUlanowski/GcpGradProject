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
    """Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r


def get_rules():
    """Getting rules for paricular token bearer 

    Raises:
        Exception: when cannot ger rules from Twitter endpoint

    Returns:
        json: response from endpoint
    """
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
    """Removing all rules

    Args:
        rules (json): rules fetched from endpoint

    Raises:
        Exception: if cannot delete already existing rules

    """
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
    """Set new rules for stream filtering       
    
    Args:
    delete (method): parsing argument           

    Raises:
        Exception: if cannot add rules to endpoint
    """
    # You can adjust the rules if needed
    sample_rules = [
        {"value": "#Trump lang:en -is:retweet", "tag": "#trump"},
        {"value": "#Biden lang:en -is:retweet", "tag": "#biden"}
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
    """Getting previously setup filterred stream of tweets

    Args:
        set (method): parsing argument

    Raises:
        Exception: if cannot get stream from endpoint

    Returns:
        string: response from an endpoint = tweet details specified in GET request
    """
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream?tweet.fields=created_at,text,lang&user.fields=name,username,description&expansions=author_id", auth=bearer_oauth, stream=True,
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
    """Parsing tweet stream to PubSub topic

    Args:
        response (string): tweet

    Returns:
        result: tweet string
    """

    publisher = pubsub_v1.PublisherClient()
    prev_tweet_id = 0 #compensating for poor Twitter API which is duplicating messages!

    def get_vals(nested, key):
        result = []
        if isinstance(nested, list) and nested != []:   #non-empty list
            for lis in nested:
                result.extend(get_vals(lis, key))
        elif isinstance(nested, dict) and nested != {}:   #non-empty dict
            for val in nested.values():
                if isinstance(val, (list, dict)):   #(list or dict) in dict
                    result.extend(get_vals(val, key))
            if key in nested.keys():   #key found in dict
                result.append(nested[key])
        return result

       
    for response_line in response.iter_lines():
        if response_line:
            tweet_proc = json.loads(response_line)
            tweet = dict(
            tweet_id = get_vals(tweet_proc, 'id')[0],\
            tweet_created_at = get_vals(tweet_proc, 'created_at')[0],\
            tweet_lang = get_vals(tweet_proc, 'lang')[0],\
            tweet_text = get_vals(tweet_proc, 'text')[0],\
            usr_descr = get_vals(tweet_proc, 'description')[0],\
            usr_id = get_vals(tweet_proc, 'id')[1],\
            usr_name = get_vals(tweet_proc, 'name')[0],\
            usr_username = get_vals(tweet_proc, 'username')[0],\
            tag = get_vals(tweet_proc, 'tag')[0]\
     )
        
        encoded_tweet = json.dumps(tweet).encode('utf-8')
        if get_vals(tweet_proc, 'id')[0] != prev_tweet_id:
            future = publisher.publish(topic_path, encoded_tweet)
            print(f'PUBLISHED MESSAGE ID: {future.result()}')
            print(tweet)
        else:
            print('duplicate!')

        prev_tweet_id = get_vals(tweet_proc, 'id')[0]



def main():
    rules = get_rules()
    delete = delete_all_rules(rules)
    set = set_rules(delete)
    response = get_stream(set)
    publish_pubsub(response)


if __name__ == "__main__":
    main()