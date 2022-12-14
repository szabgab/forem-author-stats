import requests
import os
import json
import argparse
import time

# TODO: use API key?
# TODO: Maybe compare the github_username that arrived in the JSON to the same field supplied by the user when configured the job

def collect(username, limit):
    # print(f"collect({username}, {limit})")

    page = 0
    articles = {}
    statistics = {}
    while True:
        page += 1
        url = f'https://dev.to/api/articles?username={username}&page={page}'
        #url = f'https://community.codenewbie.org/api/articles?username={username}&page={page}'
        # print(url)

        res = requests.get(url, headers = {'Accept': 'application/vnd.forem.api-v1+json'})
        print(f"Number of elements in response: {len(res.json())}")
        if len(res.json()) == 0:
            break
        for article in res.json():
            # print(article)
            articles[ article['id'] ] = article
            statistics[ article['id'] ] = {
                'comments_count': article['comments_count'],
                'public_reactions_count': article['public_reactions_count'],
                'positive_reactions_count': article['positive_reactions_count'],
            }
        if limit is not None and page >= limit:
            break

    with open('articles.json', 'w') as fh:
        json.dump(articles, fh)
    ts = int(time.time())
    with open(f'stats-{ts}.json', 'w') as fh:
        json.dump(statistics, fh)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--username',  help="The username on DEV.to")
    parser.add_argument('--limit',     help='Max number of pages to fetch', type=int)
    args = parser.parse_args()

    username = os.environ.get('DEV_TO_USERNAME')

    if args.username:
        username = args.username

    # github_username = os.environ.get('GITHUB_REPOSITORY_OWNER')

    if not username:
        exit(f"You have to supply the USERNAME either as a command line or as the environment variable DEV_TO_USERNAME")

    collect(username, args.limit)

main()

