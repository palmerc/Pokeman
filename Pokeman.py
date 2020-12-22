#!/usr/bin/env python3

from bs4 import BeautifulSoup
from requests_toolbelt.multipart.encoder import MultipartEncoder
import argparse
import pathlib
import requests
import random
import urllib.parse
import re
import os
import json
import yaml


class Pokemon:
    def __init__(self, name, number):
        self.name = name
        self.number = number

    def __str__(self):
        return f'{self.name} - {self._padded_number()}'

    def img_url(self):
        return f'https://assets.pokemon.com/assets/cms2/img/pokedex/full/{self._padded_number()}.png'

    def png(self):
        name = 'pokemon' + os.path.basename(self.img_url())
        png = requests.get(self.img_url()).content
        return name, png

    def _padded_number(self):
        return f'{int(self.number):03}'


def get_pokemen():
    pokedex = 'https://www.pokemon.com/us/pokedex/'

    request = requests.get(pokedex)
    soup = BeautifulSoup(request.text, 'html.parser')

    pokedex_re = re.compile('^National Pokédex$')
    pokemon_re = re.compile('(\d+) - (\w+)')

    pokemen = []
    for header in soup.find_all('h2', text=pokedex_re):
        ul_tag = header.findNext('ul')
        for a_tag in ul_tag.find_all('a'):
            match = re.match(pokemon_re, a_tag.text)
            number = match.group(1)
            name = match.group(2)
            pokemen.append(Pokemon(name, number))

    return pokemen


def get_pokemon(number=None):
    pokemen = get_pokemen()
    if number:
        pokemen = list(filter(lambda p: p.number == number, pokemen))
    else:
        pokemen = random.sample(pokemen, 1)

    return pokemen.pop()


def send_slack_message(token, channel, message, dryrun=False):
    url = 'https://slack.com/api/chat.postMessage'
    payload = {'token': token, 'channel': channel, 'text': message, 'as_user': True}
    if dryrun:
        print('Send message')
        print(url)
    else:
        response = requests.post(url, payload)
        print(response)


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


def post_slack_message(hook, payload, dryrun=False):
    slackurl_hook = hook

    if dryrun:
        print(slackurl_hook, payload)
    else:
        requests.post(slackurl_hook, json=payload)


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

    pokemon = get_pokemon(args.pokemon)
    print("Pokemon: {} - {}".format(pokemon.number, pokemon.name))

    if token and len(token) > 0:
        name, png = pokemon.png()
        change_slack_photo(token, name, png, dryrun=args.dryrun)
        change_slack_status(token, str(pokemon), dryrun=args.dryrun)
        send_slack_message(token, '#dev-ios', 'Good morning!', dryrun=args.dryrun)

    if qotd_hook and len(qotd_hook) > 0:
        payload = get_qotd(pokemon.name, pokemon.img_url())
        post_slack_message(qotd_hook, payload, dryrun=args.dryrun)
