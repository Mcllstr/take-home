import requests
import pandas as pd


def test_api():
    posts_df = pd.read_csv("data/posts.tsv", sep="\t", lineterminator="\n")
    posts_df = posts_df.fillna("")
    posts_data = posts_df.to_dict(orient="records")
    accounts_df = pd.read_csv("data/accounts.tsv", sep="\t", lineterminator="\n")
    accounts_df = accounts_df.fillna("")
    accounts_data = accounts_df.to_dict(orient="records")
    hashtag = "#diedsuddenly"
    url = "http://127.0.0.1:8000/synchronous_puppet_poster_pairs_count/"
    headers = {"accept": "application/json",
               "Content-Type": "application/json"}
    payload = {
        "hashtag": hashtag,
        "posts_data": posts_data[:1],
        "accounts_data": accounts_data[:1],
    }

    result = requests.post(url=url, headers=headers, json=payload)
    print(result)
    print(result.json())


if __name__ == "__main__":
    test_api()
