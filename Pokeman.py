from bs4 import BeautifulSoup
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests
import random
import json
import urllib.parse
import re

pokedex = 'https://www.pokemon.com/us/pokedex/'
pokeimg = 'https://assets.pokemon.com/assets/cms2/img/pokedex/full/{}.png'
slackurl_photo = 'https://slack.com/api/users.setPhoto?token={}&pretty=1'
slackurl_status = 'https://slack.com/api/users.profile.set?token={}&profile={}&pretty=1'
token = ''

r = requests.get(pokedex)
soup = BeautifulSoup(r.text, 'html.parser')

pokedex_re = re.compile('^National Pokédex$')
pokemon_re = re.compile('(\d+) - (\w+)')

pokenumbers = []
for header in soup.find_all('h2', text=pokedex_re):
    ul_tag = header.findNext('ul')
    for a_tag in ul_tag.find_all('a'):
        match = re.match(pokemon_re, a_tag.text)
        number = match.group(1)
        name = match.group(2)
        pokenumbers.append((number, name))

pokemon = random.sample(pokenumbers, 1).pop()
padded_number = f'{int(pokemon[0]):03}'
pokename = pokemon[1]
pokeurl = pokeimg.format(padded_number)
pokepng = requests.get(pokeurl).content

m = MultipartEncoder(fields={'image': ('pokemon{}.png'.format(padded_number), pokepng, 'image/png')})
headers = {'Content-Type': m.content_type}
requests.post(slackurl_photo.format(token), headers=headers, data=m)

pokestatus = '{} - {}'.format(padded_number, pokename)
profile = {'status_text': pokestatus}
profile_json = json.dumps(profile)
encoded_json = urllib.parse.quote(profile_json)
requests.post(slackurl_status.format(token, encoded_json))

print('Transformed to ' + pokestatus)
