#!/usr/bin/env python3

from bs4 import BeautifulSoup
from requests_toolbelt.multipart.encoder import MultipartEncoder
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


def pokemen():
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


def pokemon_pick():
    return random.sample(pokemen(), 1).pop()


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


def post_slack_qotd(hook, name, url, dryrun=False):
    slackurl_hook = hook
    r = requests.get('http://quotes.rest/qod?category=management')
    json_data = json.loads(r.text)
    if json_data:
        quote = json_data['contents']['quotes'][0]['quote']
        author = json_data['contents']['quotes'][0]['author']

    payload = {'text': '{} finds this quote inspiring...'.format(name), 'attachments': [{'author_name': author,
                                                                                         'thumb_url': url,
                                                                                         'text': quote}]}
    if dryrun:
        print('Post Slack QOTD')
        print(slackurl_hook, payload)
    else:
        requests.post(slackurl_hook, json=payload)


with open('config.yml') as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)

token = config.get('token')
qotd_hook = config.get('qotd_hook')

pokemon = pokemon_pick()

if token and len(token) > 0:
    name, png = pokemon.png()
    change_slack_photo(token, name, png)
    change_slack_status(token, str(pokemon))

if qotd_hook and len(qotd_hook) > 0:
    post_slack_qotd(qotd_hook, pokemon.name, pokemon.img_url())
