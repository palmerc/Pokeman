#!/usr/bin/env python3

from requests_toolbelt.multipart.encoder import MultipartEncoder
from datetime import datetime
import time
import argparse
import pathlib
import requests
import random
import urllib.parse
import json
import yaml

from pokemen import Pokemen


def send_slack_message(token, channel, message, at=None, dryrun=False):
    base_url = 'https://slack.com/api/'
    payload = {'token': token,
               'channel': channel,
               'text': message}

    if at:
        url = base_url + 'chat.scheduleMessage'
        payload['post_at'] = at
    else:
        url = base_url + 'chat.postMessage'

    if dryrun:
        print('Send message: "{}" at {} to {}'.format(message, at, channel))
    else:
        requests.post(url, payload)


def change_slack_photo(token, name, png, dryrun=False):
    slackurl_photo = f'https://slack.com/api/users.setPhoto?token={token}&pretty=1'
    m = MultipartEncoder(fields={'image': (name, png, 'image/png')})
    headers = {'Content-Type': m.content_type}
    url = slackurl_photo.format(token)
    if dryrun:
        print('Change Slack Photo')
        print(url)
    else:
        requests.post(url, headers=headers, data=m)


def change_slack_status(token, status, dryrun=False):
    profile = {'status_text': status}
    profile_json = json.dumps(profile)
    encoded_json = urllib.parse.quote(profile_json)
    payload = f'https://slack.com/api/users.profile.set?token={token}&profile={encoded_json}&pretty=1'
    if dryrun:
        print('Change Slack Status')
        print(payload)
    else:
        requests.post(payload)


def get_qotd(name, thumb_url):
    r = requests.get('http://quotes.rest/qod?category=management')
    json_data = json.loads(r.text)
    if json_data:
        quote = json_data['contents']['quotes'][0]['quote']
        author = json_data['contents']['quotes'][0]['author']

    payload = {'text': '{} finds this quote inspiring...'.format(name), 'attachments': [{'author_name': author,
                                                                                         'thumb_url': thumb_url,
                                                                                         'text': quote}]}
    return payload


def post_slack_message_with_hook(hook, payload, dryrun=False):
    slackurl_hook = hook

    if dryrun:
        print(slackurl_hook, payload)
    else:
        requests.post(slackurl_hook, json=payload)


def get_time_in_future():
    now = datetime.now()
    now_time = int(time.mktime(now.timetuple())) + 20
    max_time = now_time + 60 * 30
    return random.randrange(now_time, max_time)


def get_greeting():
    greetings = [
        'Top of the morning to you.',
        'Morning',
        'God morgen',
        'Bonjour',
        'Доброе утро',
        'Guten Morgen'
    ]
    for i in range(0, 20):
        greetings.extend(['Good Morning', 'good morning', 'Good morning!'])

    return random.choice(greetings)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set Slack Profile to a Pokémon')
    parser.add_argument('--config', dest='config',
                        help='set the path of the config to use', default="config.yml")
    parser.add_argument('-p', '--pokemon', dest='pokemon',
                        help='set a specific pokemon')
    parser.add_argument('-d', '--dryrun', dest='dryrun', action='store_true',
                        help='do not actually change the pokémon')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='print extra diagnostic information')
    args = parser.parse_args()

    config_path = pathlib.Path(args.config)
    with open(config_path) as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)

    token = config.get('token')
    qotd_hook = config.get('qotd_hook')
    hello_hook = config.get('hello_hook')
    if args.verbose:
        print("Token: {}". format(token))
        print("QOTD: {}". format(qotd_hook))
        print("Hello: {}". format(hello_hook))

    pokemon = Pokemen.select_pokemon(number=args.pokemon)
    print("Pokemon: {} - {}".format(pokemon.number, pokemon.name))

    if token and len(token) > 0:
        name, png = pokemon.png()
        change_slack_photo(token, name, png, dryrun=args.dryrun)
        change_slack_status(token, str(pokemon), dryrun=args.dryrun)

    if qotd_hook and len(qotd_hook) > 0:
        payload = get_qotd(pokemon.name, pokemon.img_url())
        post_slack_message_with_hook(qotd_hook, payload, dryrun=args.dryrun)
