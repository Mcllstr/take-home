from typing import List

from fastapi import FastAPI
import pandas as pd
from rapidfuzz.distance.DamerauLevenshtein import normalized_similarity
from .models import PuppetPosterRequest, PuppetPosterResponse


app = FastAPI()


def logic_hashtag_heuristic(
    hashtag: str, posts_data: List[dict], accounts_data: List[dict]
) -> int:
    posts_df = pd.DataFrame(posts_data)
    accounts_df = pd.DataFrame(accounts_data)
    posts_df["hashtags"] = posts_df["hashtags"].str.lower()
    posts_df["hashtags_list"] = posts_df["hashtags"].str.split(
        "|"
    )  # split str to list of str
    posts_df_explode = posts_df.explode("hashtags_list")  # create new rows for hashtags

    # Time delta
    posts_df_explode["timestamp"] = pd.to_datetime(posts_df_explode["created_at"])
    ds_posts = posts_df_explode[posts_df_explode["hashtags_list"] == hashtag]
    ds_posts = ds_posts.reset_index(drop=True)
    ds_posts = ds_posts.drop_duplicates(subset=["id", "hashtags_list"], keep="last")
    ds_posts = ds_posts[ds_posts["is_repost"] == False]
    ds_posts_sorted = ds_posts.sort_values(by="timestamp")
    ds_posts_sorted["time_diff"] = (
        ds_posts_sorted["timestamp"].diff().dt.total_seconds()
    )
    pairs_10_s = ds_posts_sorted[ds_posts_sorted["time_diff"] <= 10]

    pairs_10_s = pd.merge(
        pairs_10_s, accounts_df, how="left", left_on="author_id", right_on="id"
    )
    pairs_records = pairs_10_s.to_dict(orient="records")

    time_dupes = []
    seen_pairs = []
    i = 1
    for i, x in enumerate(pairs_records):
        for j, y in enumerate(pairs_records):
            if i != j:
                if set([i, j]) not in seen_pairs:
                    seen_pairs.append(set([i, j]))
                    time_delta = (x["timestamp"] - y["timestamp"]).total_seconds()
                    time_delta = abs(time_delta)
                    if time_delta <= 10:
                        time_dupes.append([x, y])

    # levenshtein scoring
    posts_with_accounts = pairs_10_s.to_dict(orient="records")

    seen_account_pairs = []
    duplicate_account_pairs = []

    for i, x in enumerate(posts_with_accounts):
        for j, y in enumerate(posts_with_accounts):
            if i != j:
                screen_name_pair = set([x["screen_name"], y["screen_name"]])
                if screen_name_pair not in seen_account_pairs:
                    seen_account_pairs.append(screen_name_pair)
                    similarity = normalized_similarity(
                        x["screen_name"], y["screen_name"]
                    )
                    if 0.8 <= similarity < 1:
                        duplicate_account_pairs.append([x, y])

    # checking similar account names against synchronous posts
    dupe_accounts_dupe_posts = []
    for x in duplicate_account_pairs:
        account_names_set = set([x[0]["screen_name"], x[1]["screen_name"]])
        for y in time_dupes:
            if account_names_set not in dupe_accounts_dupe_posts:
                post_names_set = set([y[0]["screen_name"], y[1]["screen_name"]])
                if account_names_set == post_names_set:
                    dupe_accounts_dupe_posts.append(account_names_set)

    return len(dupe_accounts_dupe_posts)


@app.post("/synchronous_puppet_poster_pairs_count/")
async def count_synchronous_puppet_poster_pairs(
    req: PuppetPosterRequest
):
    req = req.dict()
    pairs_count = logic_hashtag_heuristic(**req)
    return PuppetPosterResponse(count=pairs_count)
