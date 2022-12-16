import requests
import os
import json
import argparse
import time
import pathlib
from jinja2 import Environment, FileSystemLoader

def collect(host, limit):
    print(f"collect({host}, {limit})")

    data = pathlib.Path.cwd().joinpath('data')
    if not data.exists():
        data.mkdir()
    print(f"Data dir: {data}")

    per_page = 100

    api_key = os.environ.get('FOREM_API_KEY')
    if not api_key:
        exit("FOREM_API_KEY missing")

    page = 0
    articles = {}
    statistics = {}
    while True:
        page += 1
        url = f'https://{host}/api/articles/me?page={page}&per_page={per_page}'
        # print(url)

        headers = {'Accept': 'application/vnd.forem.api-v1+json'}
        if api_key is not None:
            headers['api-key'] = api_key

        res = requests.get(url, headers = headers)
        if res.status_code != 200:
            print(f"Failed request. Status code {res.status_code}")
            print(res.text)
            exit(1)

        print(f"Number of elements in response: {len(res.json())}")
        if len(res.json()) == 0:
            break
        for article in res.json():
            # print(article)
            del article['body_markdown']
            articles[ article['id'] ] = article
            statistics[ article['id'] ] = {
                'comments_count': article['comments_count'],
                'public_reactions_count': article['public_reactions_count'],
                'positive_reactions_count': article['positive_reactions_count'],
                'page_views_count': article['page_views_count'],
            }
        if limit is not None and page >= limit:
            break

    with open(data.joinpath('articles.json'), 'w') as fh:
        json.dump(articles, fh)
    filename = time.strftime("stats-%Y-%m-%d--%H-%M-%S.json")
    with open(data.joinpath(filename), 'w') as fh:
        json.dump(statistics, fh)

def generate_html():
    print("generate_html")

    data = pathlib.Path.cwd().joinpath('data')
    with open(data.joinpath('articles.json')) as fh:
        articles = json.load(fh)

    articles_list = sorted(articles.values(), key=lambda art: int(art['id']), reverse=True)
    tags = {}
    fields = ['page_views_count']
    for article in articles_list:
        for tag in article["tag_list"]:
            if tag not in tags:
                tags[tag] = {
                    'articles': 0,
                }
                for field in fields:
                    tags[tag][field] = 0

            tags[tag]['articles'] += 1
            for field in fields:
                tags[tag][field] += article[field]



    html = pathlib.Path.cwd().joinpath('_site')
    if not html.exists():
        html.mkdir()

    template = 'index.html'

    with open(html.joinpath('tags.json'), "w") as fh:
        json.dump(tags, fh)
    with open(html.joinpath('articles.json'), "w") as fh:
        json.dump(articles_list, fh)

    templates_dir = pathlib.Path(__file__).parent.joinpath('templates')
    env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)
    html_template = env.get_template(template)
    html_content = html_template.render(
        title = "DEV.to Analytics",
        user = articles_list[0]['user'],
        #articles = articles_list,
        #tags = tags,
    )

    with open(html.joinpath('index.html'), 'w') as fh:
        fh.write(html_content)


def commit():
    print("commit")

    os.system("git config --global user.name 'Gabor Szabo'")
    os.system("git config --global user.email 'gabor@szabgab.com'")
    os.system("git add data/")
    os.system("git commit -m 'Update collected data'")
    os.system("git push")

def get_args():
    main_parser = argparse.ArgumentParser(add_help=False)
    main_parser.add_argument('--commit',    help='Commit the downloaded data to git', action='store_true')
    main_parser.add_argument('--html',      help='Generate the HTML report', action='store_true')
    main_parser.add_argument('--collect',   help='Get the data from the Forem API', action='store_true')
    main_args, _ = main_parser.parse_known_args()
    if not main_args.commit and not main_args.html and not main_args.collect:
        main_parser.print_help()
        exit()

    parser = argparse.ArgumentParser(parents=[main_parser])
    if main_args.collect:
        #parser.add_argument('--username',  help='The username on the Forem site', required=main_args.collect)
        parser.add_argument('--host',      help='The hostname of the Forem site', required=main_args.collect)
        parser.add_argument('--limit',     help='Max number of pages to fetch', type=int)

    args = parser.parse_args()

    return args

def main():
    args = get_args()

    if args.collect:
        hosts = ('dev.to', 'community.codenewbie.org')
        if args.host not in hosts:
            exit('Invalid host')
        collect(args.host, args.limit)

    if args.commit:
        commit()

    if args.html:
        generate_html()

main()

