import requests
import os
import json
import argparse
import time
import pathlib

# TODO: use API key?
# TODO: Maybe compare the github_username that arrived in the JSON to the same field supplied by the user when configured the job

def collect(username, limit):
    print(f"collect({username}, {limit})")

    data = pathlib.Path.cwd().joinpath('data')
    if not data.exists():
        data.mkdir()
    print(f"Data dir: {data}")

    with open("README.md") as fh:
        print(fh.read())

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

    with open(data.joinpath('articles.json'), 'w') as fh:
        json.dump(articles, fh)
    ts = int(time.time())
    with open(data.joinpath(f'stats-{ts}.json'), 'w') as fh:
        json.dump(statistics, fh)

def generate_html():
    html = pathlib.Path.cwd().joinpath('_site')
    if not html.exists():
        html.mkdir()
    with open(html.joinpath('index.html'), 'w') as fh:
        fh.write("<h1>Report</h1>\n")

def commit():
    os.system("git config --global user.name 'Gabor Szabo'")
    os.system("git config --global user.email 'gabor@szabgab.com'")
    os.system("git add data/")
    os.system("git commit -m 'Update collected data'")
    os.system("git push")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--username',  help="The username on DEV.to", required=True)
    #parser.add_argument('--data',      help='The folder for the data')
    parser.add_argument('--limit',     help='Max number of pages to fetch', type=int)
    args = parser.parse_args()

    # github_username = os.environ.get('GITHUB_REPOSITORY_OWNER')

    collect(args.username, args.limit)
    commit()
    generate_html()

main()

