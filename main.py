import os
import praw
import requests
from urllib.parse import urljoin
from datetime import datetime, timedelta

from dotenv import load_dotenv

load_dotenv(override=False)

REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")
REDDIT_REFRESH_TOKEN = os.environ.get("REDDIT_REFRESH_TOKEN", "")
REDDIT_URI = os.environ.get("REDDIT_URI", "")
TWITCH_AUTH = os.environ.get("TWITCH_AUTH", "")
TWITCH_CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID", "")

class ClipNotFound(Exception):
    pass

def get_reddit():
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        refresh_token=REDDIT_REFRESH_TOKEN,
        user_agent="TibiaWars/1.0 by u/panzp",
        redirect_uri=REDDIT_URI
    )

def publish_clip(reddit, title, url):
    reddit.subreddit("tibiawars").submit(title, url=url)


def get_clips():
    half_hour_ago = datetime.now() - timedelta(minutes = 30)
    two_hour_ago = half_hour_ago - timedelta(hours = 2)
    url = urljoin(
        "https://api.twitch.tv/",
        f"helix/clips?game_id=19619&started_at={two_hour_ago.isoformat()}Z&ended_at={half_hour_ago.isoformat()}Z",
    )
    headers = {'Authorization': f'Bearer {TWITCH_AUTH}', 'Client-Id': TWITCH_CLIENT_ID}
    clips = requests.request("GET", url, headers=headers, data={}).json()
    filtered_clips = [
        clip
        for clip in clips["data"]
        if clip["language"] == "pt-br"
        and clip["view_count"] > 10
    ]
    
    if len(filtered_clips) == 0 or not filtered_clips[0].get("title"):
        raise ClipNotFound("A clip wasn't found.")
    title = f"[{filtered_clips[0]['broadcaster_name']}]  {filtered_clips[0]['title']}"
    return title, filtered_clips[0]["url"]


def main():
    title, url = get_clips()
    reddit = get_reddit()
    publish_clip(reddit, title, url)

if __name__ == "__main__":
    main()
