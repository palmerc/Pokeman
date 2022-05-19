#!/usr/bin/env python3

from requests_toolbelt.multipart.encoder import MultipartEncoder
from datetime import date, datetime
import time
import argparse
import pathlib
import requests
import random
import urllib.parse
import json
import yaml
import os

from slack_sdk import WebClient
from slack_sdk.webhook import WebhookClient

from pokemen import Pokemen
from pokemon_tcg import PokemenTCG


def get_qotd(markdown=False):
    r = requests.get('http://quotes.rest/qod?category=management')
    json_data = json.loads(r.text)
    if json_data:
        quote = json_data['contents']['quotes'][0]['quote']
        author = json_data['contents']['quotes'][0]['author']

        if markdown:
            return f'> *{author}*\n>{quote}'
        else:
            return f'{author}:\n{quote}'
    else:
        return None


def get_qotd_blocks(pokemon):
    return [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '{} finds this quote inspiring...'.format(pokemon.short_name())
            }
        },
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': get_qotd(markdown=True)
            },
            'accessory': {
                'type': 'image',
                'image_url': pokemon.img_url(),
                'alt_text': pokemon.display_name()
            }
        }
    ]


def get_card_blocks(pokemon):
    card = pokemon.random_card()
    name = card.display_name()
    title_link = '<{}|{}>'.format(card.url(), name)
    image_url = card.image()
    filename = os.path.basename(image_url)
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": title_link
            }
        },
        {
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": filename,
                "emoji": True
            },
            "image_url": image_url,
            "alt_text": name
        }
    ]


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
        'Buenas dias',
        'Доброго ранку',
        'Guten Morgen',
        'おはよう'
    ]

    # 'Доброе утро',
    today = date.today()
    new_year = date.fromisoformat('0001-01-01').replace(year=today.year)
    birthday = date.fromisoformat('1974-05-06').replace(year=today.year)
    constitution_day = date.fromisoformat('1814-05-17').replace(year=today.year)
    christmas_day = date.fromisoformat('0001-12-25').replace(year=today.year)
    if today == new_year:
        return 'Happy New Year!'
    elif today == birthday:
        return 'Happy Birthday!'
    elif today == christmas_day:
        return 'Merry Christmas!'
    elif today == constitution_day:
        return 'Gratulerer med dagen!'
    else:
        for i in range(0, 20):
            greetings.extend(['Good Morning', 'good morning', 'Good morning!'])
        return random.choice(greetings)


if __name__ == "__main__":
    source_dir = pathlib.Path(__file__).parent
    config_yml = source_dir / 'config.yml'

    parser = argparse.ArgumentParser(description='Set Slack Profile to a Pokémon') 
    parser.add_argument('--config', dest='config',
                        help='set the path of the config to use', default=str(config_yml))
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
    print(f'{date.today()}: {pokemon.display_name()}')

    if token and len(token) > 0:
        client = WebClient(token=token)

        name, png = pokemon.png()
        client.users_setPhoto(image=png)
        client.users_profile_set(profile={'status_text': pokemon.display_name()})
        client.chat_postMessage(channel='#pokecards', text=pokemon.display_name(), blocks=get_card_blocks(pokemon))
        client.chat_scheduleMessage(channel='#dev-ios',
                                    post_at=get_time_in_future(),
                                    text=get_greeting())

    if qotd_hook and len(qotd_hook) > 0:
        webhook = WebhookClient(qotd_hook)

        if not args.dryrun:
            webhook.send(blocks=get_qotd_blocks(pokemon))
